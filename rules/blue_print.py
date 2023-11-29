from input_parameter import DoubleInput
from rule_mainclass import Rule

def init_your_rule(frame, row, column):
    return YourRule(frame=frame, row=row, column=column)

class YourRule(Rule):

    def __init__(self, frame, row, column):

        self.title = "Your Rule"

        super().__init__(frame=frame, row=row, column=column, rulename=self.title)
        upcountingColumn = 3

        self.exampleVariableInput = DoubleInput(self.ruleFrame, upcountingColumn, 3.0, "Example Variable")
        upcountingColumn = upcountingColumn + 2

    def apply(self):

        # add your code here

        print("Finished applying rule {0}".format(self.title))

