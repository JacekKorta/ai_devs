from typing import Dict, List


def get_user_info_prompt(data: str, question: str) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": "Odpowiedz na pytanie otrzymane pytanie. "
            "Do odpowiedzi uzyj tylko danych z dostarczonego kontekstu:"
            "\n### Context:\n {data}".format(data=data),
        },
        {"role": "user", "content": "{question}".format(question=question)},
    ]


# unused
def get_categorise_prompt(data: str, question: str) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": """Przeczytaj uważnie otrzymane pytanie i odpowiedz jakiej osoby dotyczy
                        wybierz osobę z tabelki dołaczonej ponizej, a następnie zwróć
                        | imie | naazwisko | klucz |
                        | - | - | - |
                        | Dariusz | Kaczor | dariusz-kaczor |
                        | Katarzyna | Rumcajs | katarzyna-rumcajs |
                        | Renata | Pizza | renata-pizza |""",
        },
        {"role": "user", "content": "Po czym poznam Dariusza Kaczora"},
        {"role": "assistant", "content": "dariusz-kaczor"},
        {
            "role": "user",
            "content": "Do odpowiedzi uzyj tylko danych z dostarczonego kontekstu:"
            "\n### Context:\n {data}".format(data=data),
        },
        {"role": "user", "content": "{question}".format(question=question)},
    ]


def get_get_name_prompt(question: str) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": """Nie odpowiadaj na pytanie użytkownika. Wydobądz mi tylko Imię i nazwisko osoby z pytania.
            Jako odpowiedź zwróc tylko imie i nazwisko w nieodmienionej, pełnej (nie zdrobniałej)  formie""",
        },
        {"role": "user", "content": "gdzie mieszka Kasia Truskawka? w jakim mieście?'"},
        {"role": "assistant", "content": "Katarzyna Truskawka"},
        {"role": "user", "content": "Ulubiony kolor Witolda Marszałka, to?'"},
        {"role": "assistant", "content": "Witold Marszałek"},
        {"role": "user", "content": "{question}".format(question=question)},
    ]
