from typing import Any, List

class Student:
    def __init__(self, fname: str, sname: str, grades: List[int]):
        self.fname = fname
        self.sname = sname
        self.grades = grades

    def average_grade(self):
        return sum(self.grades) / len(self.grades)
    
    @property
    def full_name(self):
        return f"{self.fname} {self.sname}"


class Experiment:
    def __init__(self, name: str, results: List[Any], notes: str = "No notes available"):
        self.name = name
        self.results = results
        self.notes = notes

    def average_result(self):
        return sum(self.results) / len(self.results)
    
    def __str__(self):
        '''
        This method is called when we print the object. It returns a string representation of the object.
        Because of the \\033[31m and \\033[0m ANSI escape codes, the notes will be printed in red, and will only work as expected in the terminal.
        '''
        return f"This experiment is called '{self.name}'. The results from this experiment were {self.results}. Additional notes: \033[31m{self.notes}\033[0m"