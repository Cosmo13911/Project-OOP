from models.enum import SlotStatus, TournamentStatus
class ScoreRecord:
    def __init__(self, hole_number: int, stroke: int):
        self.__hole_number = hole_number
        self.__stroke = stroke

    @property
    def hole_number(self):
        return self.__hole_number

    @property
    def stroke(self):
        return self.__stroke

class Scorecard:
    def __init__(self, member, course):
        self.__member = member
        self.__course = course
        self.__scores = [] 

    @property
    def member(self): 
        return self.__member
    
    @property
    def course(self):
        return self.__course

    def record_score(self, hole_number  : int, stroke: int):
        if stroke > 0:
            for record in self.__scores:
                if record.hole_number == hole_number:
                    self.__scores.remove(record)
                    break
            
            new_record = ScoreRecord(hole_number, stroke)
            self.__scores.append(new_record)
            return True
        return False
         
    def has_recorded_scores(self):
        return len(self.__scores) > 0

    def get_gross_score(self):
        return sum(record.stroke for record in self.__scores)

    def get_course_handicap(self):
        return self.__member.current_handicap

    def get_net_score(self):
        return self.get_gross_score() - self.get_course_handicap()

    def get_cumulative_par(self):
        return self.__course.par
    
    def get_adjusted_score(self):
        return self.get_gross_score()