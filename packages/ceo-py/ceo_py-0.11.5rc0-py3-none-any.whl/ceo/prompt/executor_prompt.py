import copy
import json
import logging
from collections.abc import Iterator

from langchain_core.language_models import BaseChatModel

from ceo.ability.agentic_ability import PREFIX as AGENTIC_ABILITY_PREFIX
from ceo.ability.ability import Ability
from ceo.exception.too_dumb_exception import TooDumbException
from ceo.prompt.prompt import Prompt

log = logging.getLogger('ceo.prompt')


class ExecutorPrompt(Prompt):
    def __init__(self, args: dict, action: Ability, ext_context: str = ''):
        self.action = action
        self.args = copy.deepcopy(args)
        tmp_args = copy.deepcopy(self.args)
        if self.action.name.startswith(AGENTIC_ABILITY_PREFIX):
            del tmp_args['memory']
        prompt = json.dumps({
            "precondition": "Below is an ability shown at <ability> "
                            "and your choice(args) for using the <ability> is shown at <args(choice)>.",
            "task": "Explain what you are going to do.",
            "output_datatype": "text",
            "output_example": "I am trying to open calculator.",
            "ability": self.action.to_dict(),
            "args(choice)": tmp_args
        }, ensure_ascii=False)
        super().__init__(prompt, ext_context)
        log.debug(f'ExecutorPrompt (before): {self.prompt}')

    def explain(self, model: BaseChatModel, stream: bool = False) -> str | Iterator:
        if stream:
            return model.stream(self.prompt)
        resp = model.invoke(self.prompt).content
        log.debug(f'ExecutorResponse (before): {resp}')
        return resp

    def invoke(self, model: BaseChatModel, max_retry: int = 3) -> dict:
        result = self.action.__call__(**self.args)
        tmp_args = copy.deepcopy(self.args)
        if self.action.name.startswith(AGENTIC_ABILITY_PREFIX):
            tmp_args = {'choice': 'Ask for a favor.'}
        prompt = json.dumps({
            "precondition": "Below is an ability shown at <ability>, "
                            "your choice(args) for the <ability> is shown at <args(choice)>, "
                            "result of your using of this <ability> is shown at <result>.",
            "task": "Explain what you have done according to <ability>, <result>, and <args(choice)> "
                    "accurately, comprehensively, and briefly.",
            "ability": self.action.to_dict(),
            "args(choice)": tmp_args,
            "result": str(result),
            "output_format": {
                'ability': '{ability_just_used}',
                'choice': '{choice_just_made}',
                'returns': '{result_just_received}',
                'summarization': '{summarization}'
            },
            "output_datatype": "json",
            "output_example": json.dumps({
                'ability': 'wechat_sender',
                'choice': "{'msg': 'Bonjour'}",
                'returns': 'success',
                'summarization': "I used the wechat_sender ability to wrote a wechat message which says 'Bonjour', "
                                 "the result shows 'success' which indicates success of wechat message sending."
            }, ensure_ascii=False),
            "hint_for_output": 'You must strictly follow the json format in <output_format>!! '
                               'You can refer to example in <output_example>!!'
        }, ensure_ascii=False)
        if len(self.ext_context) > 0:
            prompt = Prompt.construct_prompt(prompt, self.ext_context)
        log.debug(f'ExecutorPrompt (after): {prompt}')
        count = 0
        exclamation = '!'
        tmp_prompt = prompt
        keys = ('summarization', 'ability', 'choice', 'returns')
        while True:
            # noinspection DuplicatedCode
            if count > 0:
                if count <= max_retry:
                    log.warning(f'ExecutorAfterPromptWarn: incorrectly formatted. Retry: {count}')
                else:
                    log.warning(f'ExecutorAfterPromptWarn: max retry exceeded.')
                    raise TooDumbException(model)
            count += 1
            res = model.invoke(tmp_prompt).content
            log.debug(f"Executor (after) thought process: \n{res}")
            try:
                correct_format = True
                res_dict: dict = json.loads(res[res.find('{'):res.rfind('}') + 1].strip())
                for _key in keys:
                    if _key not in res_dict.keys():
                        correct_format = False
                if correct_format:
                    break
                tmp_prompt = (f'{prompt}Attention_{count}: '
                              f'You must strictly follow the format in <output_format>{count * 2 * exclamation} '
                              f'You should refer to example in <output_example>{count * 2 * exclamation}')
                tmp_prompt = Prompt.construct_prompt(tmp_prompt, '')
            except json.decoder.JSONDecodeError:
                tmp_prompt = (f'{prompt}Attention_{count}: '
                              f'You must strictly follow the json format in <output_format>{count * 2 * exclamation} '
                              f'You should refer to example in <output_example>{count * 2 * exclamation}')
                tmp_prompt = Prompt.construct_prompt(tmp_prompt, '')
        return res_dict
