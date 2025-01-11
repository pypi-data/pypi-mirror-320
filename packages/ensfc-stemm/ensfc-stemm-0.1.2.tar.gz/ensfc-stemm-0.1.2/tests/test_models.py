from ensfc_stemm.models import Student, Experiment

def test_student():
    student = Student('John', 'Doe', [10, 8, 7, 9, 6])
    assert student.full_name == 'John Doe' and student.average_grade() == 8.0

def test_experiment():
    experiment = Experiment('Test experiment', [1, 2, 3, 4, 5], 'This experiment was conducted in a controlled environment.')
    assert experiment.average_result() == 3.0 and str(experiment) == "This experiment is called 'Test experiment'. The results from this experiment were [1, 2, 3, 4, 5]. Additional notes: \033[31mThis experiment was conducted in a controlled environment.\033[0m"