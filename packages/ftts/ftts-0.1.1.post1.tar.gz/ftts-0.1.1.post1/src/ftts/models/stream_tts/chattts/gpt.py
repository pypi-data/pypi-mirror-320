import torch
from dataclasses import dataclass
from typing import Optional, List, Union, Tuple, Callable
import platform
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.utils.parametrize as P
from tqdm import tqdm
from transformers import LlamaModel, LlamaConfig
from transformers.cache_utils import Cache
from transformers.modeling_outputs import BaseModelOutputWithPast
from transformers.utils import is_flash_attn_2_available

from ChatTTS.utils import del_all
from ChatTTS import model
import logging

import torch._dynamo

torch._dynamo.config.suppress_errors = True


class GPT(nn.Module):
    def __init__(
        self,
        gpt_config: dict,
        embed: model.Embed,
        use_flash_attn=False,
        use_vllm=False,
        device=torch.device("cpu"),
        device_gpt=torch.device("cpu"),
        logger=logging.getLogger(__name__),
    ):
        super().__init__()

        self.logger = logger

        self.device = device
        self.device_gpt = device_gpt

        self.generator = torch.Generator(device=device)

        self.num_vq = int(gpt_config["num_vq"])
        self.num_audio_tokens = int(gpt_config["num_audio_tokens"])
        self.num_text_tokens = int(gpt_config["num_text_tokens"])

        self.use_flash_attn = use_flash_attn
        self.is_te_llama = False
        self.is_vllm = use_vllm

        if self.is_vllm:
            return

        self.llama_config = self._build_llama_config(gpt_config)

        self.emb_code = [ec.__call__ for ec in embed.emb_code]
        self.emb_text = embed.emb_text.__call__
        self.head_text = embed.head_text.__call__
        self.head_code = [hc.__call__ for hc in embed.head_code]

    def load_pretrained(
        self, gpt_folder: str, embed_file_path: str, gpu_memory_utilization: float = 0.5
    ):
        if self.is_vllm and platform.system().lower() == "linux":
            from ChatTTS.model.velocity import LLM

            self.llm = LLM(
                model=gpt_folder,
                num_audio_tokens=self.num_audio_tokens,
                num_text_tokens=self.num_text_tokens,
                post_model_path=embed_file_path,
                gpu_memory_utilization=gpu_memory_utilization,
            )
            self.logger.info("vLLM model loaded")
            return

        self.gpt: LlamaModel = LlamaModel.from_pretrained(gpt_folder).to(
            self.device_gpt
        )
        del self.gpt.embed_tokens

    class Context:
        def __init__(self):
            self._interrupt = False

        def set(self, v: bool):
            self._interrupt = v

        def get(self) -> bool:
            return self._interrupt

    def _build_llama_config(
        self,
        config: dict,
    ) -> Tuple[LlamaModel, LlamaConfig]:
        if self.use_flash_attn and is_flash_attn_2_available():
            llama_config = LlamaConfig(
                **config,
                attn_implementation="flash_attention_2",
            )
            self.logger.warning(
                "enabling flash_attention_2 may make gpt be even slower"
            )
        else:
            llama_config = LlamaConfig(**config)

        return llama_config

    def prepare(self, compile=False):
        if self.use_flash_attn and is_flash_attn_2_available():
            self.gpt = self.gpt.to(dtype=torch.float16)
        if compile and not self.is_te_llama and not self.is_vllm:
            try:
                self.compile(backend="inductor", dynamic=True)
                self.gpt.compile(backend="inductor", dynamic=True)
            except RuntimeError as e:
                self.logger.warning(f"compile failed: {e}. fallback to normal mode.")

    @dataclass(repr=False, eq=False)
    class _GenerationInputs:
        position_ids: torch.Tensor
        cache_position: torch.Tensor
        use_cache: bool
        input_ids: Optional[torch.Tensor] = None
        past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
        attention_mask: Optional[torch.Tensor] = None
        inputs_embeds: Optional[torch.Tensor] = None

        def to(self, device: torch.device, dtype: torch.dtype):
            if self.attention_mask is not None:
                self.attention_mask = self.attention_mask.to(device, dtype=dtype)
            if self.position_ids is not None:
                self.position_ids = self.position_ids.to(device, dtype=dtype)
            if self.inputs_embeds is not None:
                self.inputs_embeds = self.inputs_embeds.to(device, dtype=dtype)
            if self.cache_position is not None:
                self.cache_position = self.cache_position.to(device, dtype=dtype)

    @torch.no_grad()
    def _prepare_generation_inputs(
        self,
        input_ids: torch.Tensor,
        past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None,
        attention_mask: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        cache_position: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        use_cache=True,
    ) -> _GenerationInputs:
        # With static cache, the `past_key_values` is None
        # TODO joao: standardize interface for the different Cache classes and remove of this if
        has_static_cache = False
        if past_key_values is None:
            if hasattr(self.gpt.layers[0], "self_attn"):
                past_key_values = getattr(
                    self.gpt.layers[0].self_attn, "past_key_value", None
                )
            has_static_cache = past_key_values is not None

        past_length = 0
        if past_key_values is not None:
            if isinstance(past_key_values, Cache):
                past_length = (
                    int(cache_position[0])
                    if cache_position is not None
                    else past_key_values.get_seq_length()
                )
                max_cache_length = past_key_values.get_max_length()
                cache_length = (
                    past_length
                    if max_cache_length is None
                    else min(max_cache_length, past_length)
                )
            # TODO joao: remove this `else` after `generate` prioritizes `Cache` objects
            else:
                cache_length = past_length = past_key_values[0][0].shape[2]
                max_cache_length = None

            # Keep only the unprocessed tokens:
            # 1 - If the length of the attention_mask exceeds the length of input_ids, then we are in a setting where
            # some of the inputs are exclusively passed as part of the cache (e.g. when passing input_embeds as
            # input)
            if (
                attention_mask is not None
                and attention_mask.shape[1] > input_ids.shape[1]
            ):
                start = attention_mask.shape[1] - past_length
                input_ids = input_ids.narrow(1, -start, start)
            # 2 - If the past_length is smaller than input_ids', then input_ids holds all input tokens. We can discard
            # input_ids based on the past_length.
            elif past_length < input_ids.shape[1]:
                input_ids = input_ids.narrow(
                    1, past_length, input_ids.size(1) - past_length
                )
            # 3 - Otherwise (past_length >= input_ids.shape[1]), let's assume input_ids only has unprocessed tokens.

            # If we are about to go beyond the maximum cache length, we need to crop the input attention mask.
            if (
                max_cache_length is not None
                and attention_mask is not None
                and cache_length + input_ids.shape[1] > max_cache_length
            ):
                attention_mask = attention_mask.narrow(
                    1, -max_cache_length, max_cache_length
                )

        if attention_mask is not None and position_ids is None:
            # create position_ids on the fly for batch generation
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask.eq(0), 1)
            if past_key_values:
                position_ids = position_ids.narrow(
                    1, -input_ids.shape[1], input_ids.shape[1]
                )

        input_length = (
            position_ids.shape[-1] if position_ids is not None else input_ids.shape[-1]
        )
        if cache_position is None:
            cache_position = torch.arange(
                past_length, past_length + input_length, device=input_ids.device
            )
        else:
            cache_position = cache_position.narrow(0, -input_length, input_length)

        if has_static_cache:
            past_key_values = None

        model_inputs = self._GenerationInputs(
            position_ids=position_ids,
            cache_position=cache_position,
            use_cache=use_cache,
        )

        # if `inputs_embeds` are passed, we only want to use them in the 1st generation step
        if inputs_embeds is not None and past_key_values is None:
            model_inputs.inputs_embeds = inputs_embeds
        else:
            # The `contiguous()` here is necessary to have a static stride during decoding. torchdynamo otherwise
            # recompiles graphs as the stride of the inputs is a guard. Ref: https://github.com/huggingface/transformers/pull/29114
            # TODO: use `next_tokens` directly instead.
            model_inputs.input_ids = input_ids.contiguous()

        model_inputs.past_key_values = past_key_values
        model_inputs.attention_mask = attention_mask

        return model_inputs

    @dataclass(repr=False, eq=False)
    class GenerationOutputs:
        ids: List[torch.Tensor]
        attentions: List[Optional[Tuple[torch.FloatTensor, ...]]]
        hiddens: List[torch.Tensor]

        def destroy(self):
            del_all(self.ids)
            del_all(self.attentions)
            del_all(self.hiddens)

    @torch.no_grad()
    def _prepare_generation_outputs(
        self,
        inputs_ids: torch.Tensor,
        start_idx: int,
        end_idx: torch.Tensor,
        attentions: List[Optional[Tuple[torch.FloatTensor, ...]]],
        hiddens: List[torch.Tensor],
        infer_text: bool,
    ) -> GenerationOutputs:
        inputs_ids = [
            inputs_ids[idx].narrow(0, start_idx, i) for idx, i in enumerate(end_idx)
        ]
        if infer_text:
            inputs_ids = [i.narrow(1, 0, 1).squeeze_(1) for i in inputs_ids]

        if len(hiddens) > 0:
            hiddens = torch.stack(hiddens, 1)
            hiddens = [
                hiddens[idx].narrow(0, 0, i) for idx, i in enumerate(end_idx.int())
            ]

        return self.GenerationOutputs(
            ids=inputs_ids,
            attentions=attentions,
            hiddens=hiddens,
        )

    @torch.no_grad()
    def generate(
        self,
        emb: torch.Tensor,
        inputs_ids: torch.Tensor,
        temperature: torch.Tensor,
        eos_token: Union[int, torch.Tensor],
        attention_mask: Optional[torch.Tensor] = None,
        max_new_token=2048,
        min_new_token=0,
        logits_processors: Tuple[
            Callable[[torch.LongTensor, torch.FloatTensor], torch.FloatTensor]
        ] = (),
        infer_text=False,
        return_attn=False,
        return_hidden=False,
        stream=False,
        show_tqdm=True,
        ensure_non_empty=True,
        stream_batch=24,
        manual_seed: Optional[int] = None,
        context=Context(),
    ):
        attentions: List[Optional[Tuple[torch.FloatTensor, ...]]] = []
        hiddens = []
        stream_iter = 0

        start_idx, end_idx = (
            inputs_ids.shape[1],
            torch.zeros(
                inputs_ids.shape[0], device=inputs_ids.device, dtype=torch.long
            ),
        )
        finish = torch.zeros(inputs_ids.shape[0], device=inputs_ids.device).bool()

        old_temperature = temperature

        temperature = (
            temperature.unsqueeze(0)
            .expand(inputs_ids.shape[0], -1)
            .contiguous()
            .view(-1, 1)
        )

        attention_mask_cache = torch.ones(
            (
                inputs_ids.shape[0],
                inputs_ids.shape[1] + max_new_token,
            ),
            dtype=torch.bool,
            device=inputs_ids.device,
        )
        if attention_mask is not None:
            attention_mask_cache.narrow(1, 0, attention_mask.shape[1]).copy_(
                attention_mask
            )

        progress = inputs_ids.size(1)
        # pre-allocate inputs_ids
        inputs_ids_buf = torch.zeros(
            inputs_ids.size(0),
            progress + max_new_token,
            inputs_ids.size(2),
            dtype=inputs_ids.dtype,
            device=inputs_ids.device,
        )
        inputs_ids_buf.narrow(1, 0, progress).copy_(inputs_ids)
        del inputs_ids
        inputs_ids = inputs_ids_buf.narrow(1, 0, progress)

        pbar: Optional[tqdm] = None

        if show_tqdm:
            pbar = tqdm(
                total=max_new_token,
                desc="text" if infer_text else "code",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}(max) [{elapsed}, {rate_fmt}{postfix}]",
            )

        past_key_values = None

        for i in range(max_new_token):
            model_input = self._prepare_generation_inputs(
                inputs_ids,
                past_key_values,
                attention_mask_cache.narrow(1, 0, inputs_ids.shape[1]),
                use_cache=not self.is_te_llama,
            )

            if i > 0:
                del emb
                inputs_ids_emb = model_input.input_ids.to(self.device_gpt)
                if infer_text:
                    emb: torch.Tensor = self.emb_text(inputs_ids_emb[:, :, 0])
                else:
                    code_emb = [
                        self.emb_code[i](inputs_ids_emb[:, :, i])
                        for i in range(self.num_vq)
                    ]
                    emb = torch.stack(code_emb, 3).sum(3)
                del inputs_ids_emb, model_input.input_ids
            model_input.inputs_embeds = emb

            model_input.to(self.device_gpt, self.gpt.dtype)

            outputs: BaseModelOutputWithPast = self.gpt(
                attention_mask=model_input.attention_mask,
                position_ids=model_input.position_ids,
                past_key_values=model_input.past_key_values,
                inputs_embeds=model_input.inputs_embeds,
                use_cache=model_input.use_cache,
                output_attentions=return_attn,
                cache_position=model_input.cache_position,
            )
            del_all(model_input)
            attentions.append(outputs.attentions)
            hidden_states = outputs.last_hidden_state.to(
                self.device, dtype=torch.float
            )  # 🐻
            past_key_values = outputs.past_key_values
            del_all(outputs)
            if return_hidden:
                hiddens.append(hidden_states.narrow(1, -1, 1).squeeze_(1))

            with P.cached():
                if infer_text:
                    logits: torch.Tensor = self.head_text(hidden_states)
                else:
                    # logits = torch.stack([self.head_code[i](hidden_states) for i in range(self.num_vq)], 3)
                    logits = torch.empty(
                        hidden_states.size(0),
                        hidden_states.size(1),
                        self.num_audio_tokens,
                        self.num_vq,
                        dtype=torch.float,
                        device=self.device,
                    )
                    for num_vq_iter in range(self.num_vq):
                        x: torch.Tensor = self.head_code[num_vq_iter](hidden_states)
                        logits[..., num_vq_iter] = x
                        del x

            del hidden_states

            # logits = logits[:, -1].float()
            logits = logits.narrow(1, -1, 1).squeeze_(1).float()

            if not infer_text:
                # logits = rearrange(logits, "b c n -> (b n) c")
                logits = logits.permute(0, 2, 1)
                logits = logits.reshape(-1, logits.size(2))
                # logits_token = rearrange(inputs_ids[:, start_idx:], "b c n -> (b n) c")
                inputs_ids_sliced = inputs_ids.narrow(
                    1,
                    start_idx,
                    inputs_ids.size(1) - start_idx,
                ).permute(0, 2, 1)
                logits_token = inputs_ids_sliced.reshape(
                    inputs_ids_sliced.size(0) * inputs_ids_sliced.size(1),
                    -1,
                ).to(self.device)
                del inputs_ids_sliced
            else:
                logits_token = (
                    inputs_ids.narrow(
                        1,
                        start_idx,
                        inputs_ids.size(1) - start_idx,
                    )
                    .narrow(2, 0, 1)
                    .to(self.device)
                )

            logits /= temperature

            for logitsProcessors in logits_processors:
                logits = logitsProcessors(logits_token, logits)

            del logits_token

            if i < min_new_token:
                logits[:, eos_token] = -torch.inf

            scores = F.softmax(logits, dim=-1)

            del logits

            if manual_seed is None:
                idx_next = torch.multinomial(scores, num_samples=1).to(finish.device)
            else:
                idx_next = torch.multinomial(
                    scores,
                    num_samples=1,
                    generator=self.generator.manual_seed(manual_seed),
                ).to(finish.device)

            del scores

            if not infer_text:
                # idx_next = rearrange(idx_next, "(b n) 1 -> b n", n=self.num_vq)
                idx_next = idx_next.view(-1, self.num_vq)
                finish_or = idx_next.eq(eos_token).any(1)
                finish.logical_or_(finish_or)
                del finish_or
                inputs_ids_buf.narrow(1, progress, 1).copy_(idx_next.unsqueeze_(1))
            else:
                finish_or = idx_next.eq(eos_token).any(1)
                finish.logical_or_(finish_or)
                del finish_or
                inputs_ids_buf.narrow(1, progress, 1).copy_(
                    idx_next.unsqueeze_(-1).expand(-1, -1, self.num_vq),
                )

            if i == 0 and finish.any():
                self.logger.warning(
                    "unexpected end at index %s",
                    str([unexpected_idx.item() for unexpected_idx in finish.nonzero()]),
                )
                if ensure_non_empty and manual_seed is None:
                    if show_tqdm:
                        pbar.close()
                    self.logger.warning("regenerate in order to ensure non-empty")
                    del_all(attentions)
                    del_all(hiddens)
                    del (
                        start_idx,
                        end_idx,
                        finish,
                        temperature,
                        attention_mask_cache,
                        past_key_values,
                        idx_next,
                        inputs_ids_buf,
                    )
                    new_gen = self.generate(
                        emb,
                        inputs_ids,
                        old_temperature,
                        eos_token,
                        attention_mask,
                        max_new_token,
                        min_new_token,
                        logits_processors,
                        infer_text,
                        return_attn,
                        return_hidden,
                        stream,
                        show_tqdm,
                        ensure_non_empty,
                        stream_batch,
                        manual_seed,
                        context,
                    )
                    for result in new_gen:
                        yield result
                    del inputs_ids
                return

            del idx_next
            progress += 1
            inputs_ids = inputs_ids_buf.narrow(1, 0, progress)

            not_finished = finish.logical_not().to(end_idx.device)
            end_idx.add_(not_finished.int())
            stream_iter += not_finished.any().int()
            if stream:
                if stream_iter > 0 and stream_iter % stream_batch == 0:
                    self.logger.debug("yield stream result, end: %d", end_idx)
                    yield self._prepare_generation_outputs(
                        inputs_ids,
                        start_idx,
                        end_idx,
                        attentions,
                        hiddens,
                        infer_text,
                    )
            del not_finished

            if finish.all() or context.get():
                break

            if pbar is not None:
                pbar.update(1)

        if pbar is not None:
            pbar.close()

        if not finish.all():
            if context.get():
                self.logger.warning("generation is interrupted")
            else:
                self.logger.warning(
                    f"incomplete result. hit max_new_token: {max_new_token}"
                )

        del finish, inputs_ids_buf

        yield self._prepare_generation_outputs(
            inputs_ids,
            start_idx,
            end_idx,
            attentions,
            hiddens,
            infer_text,
        )


@dataclass(repr=False, eq=False)
class RefineTextParams:
    prompt: str = ""
    top_P: float = 0.7
    top_K: int = 20
    temperature: float = 0.7
    repetition_penalty: float = 1.0
    max_new_token: int = 384
    min_new_token: int = 0
    show_tqdm: bool = True
    ensure_non_empty: bool = True
    manual_seed: Optional[int] = None


class Embed(model.Embed):
    def __init__(
        self,
        hidden_size,
        num_audio_tokens,
        num_text_tokens,
        num_vq,
        model_path,
        device="cpu",
    ):
        super().__init__(hidden_size, num_audio_tokens, num_text_tokens, num_vq)
        self.load_pretrained(model_path, device=device)


class StreamGPT(GPT):
    def __init__(
        self,
        config,
        embed_path,
        model_path,
        tokenizer_path,
        top_k=20,
        top_p=0.7,
        temperature=0.1,
        repetition_penalty=1.05,
        min_new_token=0,
        max_new_token=2048,
        manual_seed=None,
        compile=False,
        device="cpu",
        use_vllm=False,
        gpu_memory_utilization=0.5,
    ):
        spk_stat = "愐穤巩噅廷戇笉屈癐媄垹垧帶爲漈塀殐慄亅倴庲舴猂瑈圐狴夥圓帍戛挠腉耐劤坽喳幾战謇聀崒栄呥倸庭燡欈杁襐褄乭埗幺爃弔摁斐捔兕佖廐舏竾豃磐姓趡佄幒爚欄豄讐皳訵仩帆投謌荃蝐叄圝伆幦抂茁呄掑斃讹傮庞爣蜀橁偐祄亥兡常爂欍扉丐浔佱僈強払伅扂蛐徴憍傞巀戺欀艂琐嗴啥値彷刂權穈扒卤俔贲庛初笂卄贐枴仭亁庛剎猢扃缐趤刁偵幪舏伌煁婐潤晍位弾舙茥穁葏蠣訑企庤刊笍橁溑僔云偁庯戚伍潉膐脴僵噔廃艅匊祂唐憴壝嗙席爥欁虁谐牴帽势弿牳蜁兀蛐傄喩丿帔刔圆衁廐罤庁促帙劢伈汄樐檄勵伴弝舑欍罅虐昴劭勅帜刼朊蕁虐蓴樑伫幨扑謪剀堐稴丵伱弐舮諸赁習俔容厱幫牶謃孄糐答嗝僊帜燲笄終瀒判久僤帘爴茇千孑冄凕佳引扐蜁歁缏裄剽儺恘爋朏眿廐呄塍嘇幻爱茠詁訐剴唭俐幾戊欀硁菐贄楕偒巡爀弎屄莐睳賙凶彎刅漄區唐溴剑劋庽舽猄煃跐夔惥伾庮舎伈罁垑坄怅业怯刁朇獁嶏覔坩俳巶爜朐潁崐萄俹凛常爺笌穀聐此夡倛帡刀匉終窏舣販侽怿扉伥贿憐忓謩姆幌犊漂慆癒却甝兎帼戏欅詂浐朔仹壭帰臷弎恇菐獤帡偖帘爞伅腂皐纤囅充幓戠伥灂丐訤戱倱弋爮嬌癁恐孄侥劬忶刓國詀桒古偩嘄庬戚茝赂监燤嘑勌幦舽持呂諐棤姑再底舡笍艃瀐孴倉傔弋爔猠乁濑塄偽嘧恂舛缇襃厐窴仡刱忕別漇穁岏缴廽价庌爊謈硄讑惤倁儂庭爋伇蝂嶐莔摝傠库刞茄歃戏薤伍伯廮创笠塄熐兴勽俄帅剉最腀砐敤卝侍弆戺朒虃旐蚄梕亖幔牻朣扅贐玔堝噅帡剌圅摀崐彤流僳庙爖嬇啁渐悤堁丛幆刧挜彃悐幤刹嚟恕芁看聀摐焔向乁帖爭欁癃糒圄弙佱廜戤謍婀咐昴焍亩廦艏拼謿芐癤怹兽幸舳朇畁喐稔毝丼弈懲挀譂勑哴啁伎常舭笯晁堑俄叩剔廟爍欦絁夒伤休傑廳戌蜅潆癐彴摑勯床刽欅艁砐忄搉从廡舊猥潂唐委仱僜廼爤朄呃弐礔滵垓幩爄挂筁乐籤刕凟幵爠弉癅乑吴勥伖帪舩茆婁碐幤叭乢巜艳猁桀桐啄唩俊幍舮猀艅焐螔琽亀帋爜缅噃咐斤喩予幩爛笆摀浐猴依侹幃刕園慄蛐栤澹仑座爼謉桃慐浔斕偻幛懰嬓衁愐氄悅仿应芔漄衃敐謤傁匩幹抃圉癄廐裄屵噉幍利謍聂搐蛔嚙坍怗舁圐畃膐栄刵东巆戤諾呃偑媤嗨跞忶爝眄祂朒嶔僭劉忾刐匋癄袐翴珅僷廲芄茈恈皐擄崑伄廉牍匃剃犏澤唑丄庺戃伃煀某杄偙亽帴切缌罄挐尴噙倰带舞漄橄塐糴俩僯帀般漀坂栐更両俇廱舌猁慂拐偤嶱卶应刪眉獁茐伔嘅偺帟舊漂恀栐暄喡乞庙舆匂敀潑恔劑侖延戦盽怶唯慳蝘蟃孫娎益袰玍屃痶翮笪儚裀倹椌玻翀詵筽舘惯堿某侰晈藏缮詗廦夸妎瑻瀒裔媀憞唃冶璭狻渠荑奬熹茅愺氰菣滠翦岓褌泣崲嚭欓湒聙宺爄蛅愸庍匃帆誔穮懌蓪玷澌氋抌訙屌臞廛玸听屺希疭孝凂紋新煎彃膲跱尪懁眆窴珏卓揨菸紭概囥显壌榄垫嘮嬭覤媸侵佮烒耸觌婀秋狃帹葯訤桜糨笾腢伀肶悍炂艤禖岅臺惘梷瞍友盁佨岧憳瓧嘴汬藊愌蘤嶠硴绤蜲襏括勾谂縨妥蓪澭竭萢藜纞糲煮愆瀯孯琓罂諺塿燗狟弙衯揻縷丱糅臄梱瀮杰巳猙亊符胠匃泀廏圃膂蒃籏礩岈簹缌劺燲褡孓膜拔蠿觮呋煣厌尷熜論弲牭紫寊誃紀橴賬傸箍弚窃侫簲慯烣渽祌壓媥噜夽夛諛玹疮禄冪謇媽衤盰缺繑薫兾萧嵱打滽箺嚯凣狢蠜崼覽烸簶盯籓摀苶峸懗泲涻凮愳緗剋笔懆廡瞿椏礤惐藥崍腈烄伹亯昣翬褍絋桫僨吨莌丛矄蜞娈憊苆塁蓏嚢嫼绻崱婋囱蠸篯晣芀繼索兓僖誹岯圪褰蠇唓妷胅巁渮砛傈蝷嵚冃購赁峍裋荂舾符熻岳墩寮粃凲袑彚太绲头摯繳狁俥籌冝諝註坎幫擤詒宒凕賐唶梎噔弼課屿覍囨焬櫱撪蝮蝬簸懰櫫涺嵍睻屪翔峞慘滟熲昱军烊舿尦舄糖奁溏凂彆蝲糴禍困皻灏牋睒诙嶱臀开蓈眎腼丢纻廏憤嫖暭袭崲肸螛妒榗紉谨窮袃瑠聍绊腆亿冲葐喋縔詖岑兾给堸赏旻桀蛨媆訂峦紷敯囬偐筨岸焸拭笵殒哜墒萍屓娓諙械臮望摰芑寭准僞谹氍旋憢菮屃划欣瘫谎蘻哐繁籥禦僿誵皯墓燀縿笞熦绗稹榎矻綞蓓帡戓沺区才畃洊詪糐裶盰窶耎偌劂誐庩惝滜沺哮呃煐譠崄槀猄肼蔐擋湌蠺篃恥諌瞦宍堫挪裕崑慩狲悠煋仛愞砈粵八棁害楐妋萔貨尵奂苰怫誎傫岆蕯屇脉夈仆茎刓繸芺壸碗曛汁戭炻獻凉媁兎狜爴怰賃纎袏娷禃蓥膹薪渻罸窿粫凾褄舺窮墫干苊繁冏僮訸夯绛蓪虛羽慲烏憷趎睊蠰莍塞成廎盁欏喓蜮譤崆楁囘矇薭伣艘虝帴奮苢渶虎暣翐蝃尾稈糶瀴罐嵚氮葯笫慐棌悶炯竻爅们媡姢嫺窷刮歫劈裩屬椕賑蜹薊刲義哯尗褦瓀稾礋揣窼舫尋姁椄侸嗫珺修纘媃腽蛛稹梭呛瀈蘟縀礉論夵售主梮蠉娅娭裀誼嶭観枳倊簈褃擞綿催瞃溶苊笛襹櫲盅六囫獩佃粨慯瓢眸旱荃婨蔞岋祗墼焻网牻琖詆峋秉胳媴袭澓賢経稟壩胫碯偏囫嶎纆窈槊賐撹璬莃缘誾宭愊眗喷监劋萘訯總槿棭戾墮犄恌縈簍樥蛔杁袭嫛憫倆篏墵賈羯茎觳蒜致娢慄勒覸蘍曲栂葭宆妋皽缽免盳猼蔂糥觧烳檸佯憓煶蔐筼种繷琲膌塄剰讎対腕棥渽忲俛浪譬秛惛壒嘸淫冻曄睻砃奫貯庴爅粓脮脡娎妖峵蘲討惋泊蠀㴆"
        embed = Embed(
            config["hidden_size"],
            config["num_audio_tokens"],
            config["num_text_tokens"],
            config["num_vq"],
            embed_path,
            device,
        )
        super().__init__(
            gpt_config=config,
            embed=embed,
            use_flash_attn=False,
            use_vllm=use_vllm,
            device=device,
            device_gpt=device,
        )
        self.eval()
        self.load_pretrained(
            model_path, embed_path, gpu_memory_utilization=gpu_memory_utilization
        )
        if compile and "cuda" in device:
            self.prepare(compile=compile)

        self.config = config
        self.device = device
        self.embed = embed
        self.speaker = model.Speaker(config["hidden_size"], spk_stat, device)
        self.tokenizer = model.Tokenizer(tokenizer_path)

        self.num_code = config["num_audio_tokens"] - 1
        logits_warpers, logits_processors = model.gen_logits(
            num_code=self.num_code,
            top_P=top_p,
            top_K=top_k,
            repetition_penalty=repetition_penalty,
        )
        self.logits_processors = (*logits_processors, *logits_warpers)
        self.temperature = torch.tensor([temperature] * config["num_vq"], device=device)
        self.max_new_token = max_new_token
        self.min_new_token = min_new_token
        self.manual_seed = manual_seed
        self.random_spk_emb = self.speaker.sample_random()

    def generate(
        self, text, spk_emb=None, speech_tokens=None, prompt="", speed: int = 5
    ):
        prompt = f"{prompt}[speed_{speed}]"
        spk_emb = spk_emb or self.random_spk_emb
        text = self.speaker.decorate_code_prompts(
            [text], prompt=prompt, txt_smp=None, spk_emb=spk_emb
        )
        # speech_tokens: dvae.encode(wav)
        if speech_tokens is not None:
            speech_tokens = self.speaker.decode_prompt(speech_tokens)
        input_ids, attention_mask, text_mask = self.tokenizer.encode(
            text, self.config["num_vq"], speech_tokens, self.device
        )
        emb = self.embed(input_ids, text_mask)
        if spk_emb is not None:
            self.speaker.apply(
                emb,
                spk_emb,
                input_ids,
                self.tokenizer.spk_emb_ids,
                self.device,
            )

        num_tokens = 0
        for tokens in super().generate(
            emb,
            input_ids,
            temperature=self.temperature,
            eos_token=self.num_code,
            attention_mask=attention_mask,
            max_new_token=self.max_new_token,
            min_new_token=self.min_new_token,
            logits_processors=self.logits_processors,
            infer_text=False,
            return_hidden=True,
            stream=True,
            show_tqdm=True,
            ensure_non_empty=True,
            stream_batch=4,
            manual_seed=self.manual_seed,
        ):
            ids = tokens.ids[0].T[None, :, num_tokens:]
            num_tokens += ids.shape[2]
            yield ids

    def refine_text(
        self,
        text,
        params: RefineTextParams = RefineTextParams(
            prompt="[oral_7][laugh_0][break_6]"
        ),
    ):
        if not isinstance(text, list):
            text = [text]

        input_ids, attention_mask, text_mask = self.tokenizer.encode(
            text=self.speaker.decorate_text_prompts(text, params.prompt),
            num_vq=self.config["num_vq"],
            device=self.device_gpt,
        )

        logits_warpers, logits_processors = model.gen_logits(
            num_code=self.tokenizer.len,
            top_P=params.top_P,
            top_K=params.top_K,
            repetition_penalty=params.repetition_penalty,
        )

        emb = self.embed(input_ids, text_mask)

        del text_mask

        result = next(
            super().generate(
                emb,
                input_ids,
                temperature=torch.tensor([params.temperature], device=self.device),
                eos_token=self.tokenizer.eos_token,
                attention_mask=attention_mask,
                max_new_token=params.max_new_token,
                min_new_token=params.min_new_token,
                logits_processors=(*logits_processors, *logits_warpers),
                infer_text=True,
                stream=False,
                show_tqdm=params.show_tqdm,
                ensure_non_empty=params.ensure_non_empty,
                manual_seed=params.manual_seed,
            )
        )

        del emb, input_ids

        text_tokens = result.ids
        text_tokens = [i[i.less(self.tokenizer.break_0_ids)] for i in text_tokens]
        text = self.tokenizer.decode(text_tokens)
        result.destroy()
        return text[0]

    def load_pretrained(
        self, gpt_folder: str, embed_file_path: str, gpu_memory_utilization: float = 0.5
    ):
        if self.is_vllm and platform.system().lower() == "linux":
            from ChatTTS.model.velocity import LLM

            self.llm = LLM(
                model=gpt_folder,
                num_audio_tokens=self.num_audio_tokens,
                num_text_tokens=self.num_text_tokens,
                post_model_path=embed_file_path,
                gpu_memory_utilization=gpu_memory_utilization,
            )
            self.logger.info("vLLM model loaded")
            return

        self.gpt: LlamaModel = LlamaModel.from_pretrained(gpt_folder).to(
            self.device_gpt
        )
        del self.gpt.embed_tokens
