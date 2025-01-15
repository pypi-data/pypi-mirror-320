class Course:

    def __init__(self, name, duration, link):
        self.name = name
        self.duration = duration
        self.link = link

    def __repr__(self):
        return f"'{self.name}' tiene una duracion de [{self.duration} horas] ------> {self.link}"

courses = [
    Course("Introdución a Linux", 15, "www.es"),
    Course("Personalización de Linux", 3, "www.es"),
    Course("Introdución al Hacking", 53, "www.es"),
    Course("Python Ofensivo", 50, "www.es")
]

def list_courses():
    for course in courses:
        print(course)

def find_course(curso):
    for course in courses:
        if course.name == curso:
            return course
    return None







