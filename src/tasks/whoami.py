import time
from pprint import pprint
from typing import Dict, List, Optional

from openai import OpenAI
from pydantic import BaseModel

from src import utils
from src.exceptions import StoppedByModeration
from src.openai_utils import is_flagged
from src.settings import get_settings

TASK_NAME: str = "whoami"
settings = get_settings()
client: OpenAI = OpenAI(api_key=settings.openai_api_key)

NO_ANSWER_KEY = "NEXT"

MESSAGES = [
    {
        "role": "system",
        "content": "Wciel się w role uczestnika teleturnieju. W kolejnych wiadomościach ode mnie będziesz "
        "dostawał informacje o pewnej postaci. Twoim zadaniem jest odgadnięcie kim jest ta postać. "
        "Wygrasz jeśli zgadniesz, ale przegrasz jeśli podasz nieprawidłowa odpowiedź. "
        f"Jeśli nie jesteś pewien kto to, powiedz: '{NO_ANSWER_KEY}' i nic więcej.\n "
        "Jeśli jesteś pewien kto to: Podaj jego imie i nazwisko.\n"
        "\nPotwierdź ze zrozumiałeś pisząc '...' i nic więcej",
    },
    {"role": "assistant", "content": "..."},
]


class TaskResponse(BaseModel):
    code: int
    msg: str
    hint: Optional[str] = None
    answer: Optional[str] = None


def get_answer_from_model(current_messages: List[dict]) -> str:
    response = client.chat.completions.create(
        temperature=0.3, model="gpt-3.5-turbo", messages=current_messages
    )
    return response.choices[0].message.content


def solve(task_name: str) -> None:
    has_answer = False
    current_messages = MESSAGES
    hints = set()
    while not has_answer:
        answer = None
        token_url: str = utils.get_token_url(task_name)
        token: str = utils.get_token(token_url)
        task_url: str = utils.get_task_url(token)
        task_obj = TaskResponse(**utils.get_task(task_url).json())
        hint = task_obj.hint
        if is_flagged([hint]):
            raise StoppedByModeration(f"{hint} Was stopped by moderation!")
        print(f"Received hint: {hint}")
        if hint not in hints:
            hints.add(task_obj.hint)
            msg: Dict = {"role": "user", "content": hint}
            current_messages.append(msg)
            answer = get_answer_from_model(current_messages)
            print(f"Answer from model: {answer}")
        else:
            print(f"Hint: '{hint}' is not new. Current Hints set: {hints}")
        if answer and answer.lower() != NO_ANSWER_KEY.lower():
            has_answer = True
            utils.send_answer(token=token, answer=answer)
        else:
            print("Answer not send")
            print("**" * 10)
            print("Current conversation:")
            pprint(current_messages)
            time.sleep(2)


if __name__ == "__main__":
    # utils.print_task(TASK_NAME)
    solve(TASK_NAME)


###### Przebieg zadania:

# Received hint: często chodził boso po biurze
# Answer from model: NEXT
# Answer not send
# ********************
# Current conversation:
# [{'content': 'Wciel się w role uczestnika teleturnieju. W kolejnych '
#              'wiadomościach ode mnie będziesz dostawał informacje o pewnej '
#              'postaci. Twoim zadaniem jest odgadnięcie kim jest ta postać. '
#              'Wygrasz jeśli zgadniesz, ale przegrasz jeśli podasz '
#              'nieprawidłowa odpowiedź. Jeśli nie jesteś pewien kto to, '
#              "powiedz: 'NEXT' i nic więcej.\n"
#              ' Jeśli jesteś pewien kto to: Podaj jego imie i nazwisko.\n'
#              '\n'
#              "Potwierdź ze zrozumiałeś pisząc '...' i nic więcej",
#   'role': 'system'},
#  {'content': '...', 'role': 'assistant'},
#  {'content': 'często chodził boso po biurze', 'role': 'user'}]
# Received hint: W momencie śmierci, jego majątek był szacowany na około 10,2 miliarda dolarów
# Answer from model: NEXT
# Answer not send
# ********************
# Current conversation:
# [{'content': 'Wciel się w role uczestnika teleturnieju. W kolejnych '
#              'wiadomościach ode mnie będziesz dostawał informacje o pewnej '
#              'postaci. Twoim zadaniem jest odgadnięcie kim jest ta postać. '
#              'Wygrasz jeśli zgadniesz, ale przegrasz jeśli podasz '
#              'nieprawidłowa odpowiedź. Jeśli nie jesteś pewien kto to, '
#              "powiedz: 'NEXT' i nic więcej.\n"
#              ' Jeśli jesteś pewien kto to: Podaj jego imie i nazwisko.\n'
#              '\n'
#              "Potwierdź ze zrozumiałeś pisząc '...' i nic więcej",
#   'role': 'system'},
#  {'content': '...', 'role': 'assistant'},
#  {'content': 'często chodził boso po biurze', 'role': 'user'},
#  {'content': 'W momencie śmierci, jego majątek był szacowany na około 10,2 '
#              'miliarda dolarów',
#   'role': 'user'}]
# Received hint: W momencie śmierci, jego majątek był szacowany na około 10,2 miliarda dolarów
# Hint: `W momencie śmierci, jego majątek był szacowany na około 10,2 miliarda dolarów` is not new. Current Hints set: {'często chodził boso po biurze', 'W momencie śmierci, jego majątek był szacowany na około 10,2 miliarda dolarów'}
# Answer not send
# ********************
# Current conversation:
# [{'content': 'Wciel się w role uczestnika teleturnieju. W kolejnych '
#              'wiadomościach ode mnie będziesz dostawał informacje o pewnej '
#              'postaci. Twoim zadaniem jest odgadnięcie kim jest ta postać. '
#              'Wygrasz jeśli zgadniesz, ale przegrasz jeśli podasz '
#              'nieprawidłowa odpowiedź. Jeśli nie jesteś pewien kto to, '
#              "powiedz: 'NEXT' i nic więcej.\n"
#              ' Jeśli jesteś pewien kto to: Podaj jego imie i nazwisko.\n'
#              '\n'
#              "Potwierdź ze zrozumiałeś pisząc '...' i nic więcej",
#   'role': 'system'},
#  {'content': '...', 'role': 'assistant'},
#  {'content': 'często chodził boso po biurze', 'role': 'user'},
#  {'content': 'W momencie śmierci, jego majątek był szacowany na około 10,2 '
#              'miliarda dolarów',
#   'role': 'user'}]
# Received hint: często nosił jeansy i buty typu sneakers New Balance
# Answer from model: NEXT
# Answer not send
# ********************
# Current conversation:
# [{'content': 'Wciel się w role uczestnika teleturnieju. W kolejnych '
#              'wiadomościach ode mnie będziesz dostawał informacje o pewnej '
#              'postaci. Twoim zadaniem jest odgadnięcie kim jest ta postać. '
#              'Wygrasz jeśli zgadniesz, ale przegrasz jeśli podasz '
#              'nieprawidłowa odpowiedź. Jeśli nie jesteś pewien kto to, '
#              "powiedz: 'NEXT' i nic więcej.\n"
#              ' Jeśli jesteś pewien kto to: Podaj jego imie i nazwisko.\n'
#              '\n'
#              "Potwierdź ze zrozumiałeś pisząc '...' i nic więcej",
#   'role': 'system'},
#  {'content': '...', 'role': 'assistant'},
#  {'content': 'często chodził boso po biurze', 'role': 'user'},
#  {'content': 'W momencie śmierci, jego majątek był szacowany na około 10,2 '
#              'miliarda dolarów',
#   'role': 'user'},
#  {'content': 'często nosił jeansy i buty typu sneakers New Balance',
#   'role': 'user'}]
# Received hint: został wyrzucony z własnej firmy 1985 roku
# Answer from model: Steve Jobs
# {'code': 0, 'msg': 'OK', 'note': 'CORRECT'}
