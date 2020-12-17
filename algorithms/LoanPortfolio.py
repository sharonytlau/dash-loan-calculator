class LoanPortfolio:
    """ Portfolio of Loans class
    """

    def __init__(self):
        """ Constructor to setup a portfolio of loans.
        """
        self.loans = []
        self.schedule = {}
        self.total_principal_paid = 0.0
        self.total_interest_paid = 0.0
        self.time_to_loan_termination = None

    def add_loan(self, loan):  # loan is a Loan() instance
        """ Add a loan to the portfolio
            :param loan: single loan
        """
        self.loans.append(loan)

    def remove_last_loan(self):
        """ Remove the last loan within the portfolio
        """
        self.loans.pop(-1)

    def get_loan_count(self):
        """ Return the number of loans in the portfolio
            :return: number of loans in the portfolio
        """
        return len(self.loans)

    def aggregate(self):
        """ Aggregate the loans within the portfolio by creating a schedule that includes all loans.
            :return: None, the schedule is stored in an instance dictionary
        """
        for loan in self.loans:
            for key, pay in loan.schedule.items():
                if key not in self.schedule.keys():
                    self.schedule[key] = (key, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                begin_principal = self.schedule[key][1] + pay[1]
                payment = self.schedule[key][2] + pay[2]
                extra_payment = self.schedule[key][3] + pay[3]
                applied_principal = self.schedule[key][4] + pay[4]
                applied_interest = self.schedule[key][5] + pay[5]
                end_principal = self.schedule[key][6] + pay[6]
                self.schedule[key] = (key, begin_principal, payment, extra_payment,
                                      applied_principal, applied_interest, end_principal)
            self.time_to_loan_termination = len(self.schedule)
            self.total_principal_paid += loan.total_principal_paid
            self.total_interest_paid  += loan.total_interest_paid

    def compute_impact(self):  ################################### ???
        """ Compute the difference in two loans.
            :return: differences in time to loan termination and interest paid between the overall and contributor
        """
        time_to_loan_termination_all = self.loans[0].time_to_loan_termination
        total_interest_paid_all = self.loans[0].total_interest_paid

        time_to_loan_termination_contributor = self.loans[1].time_to_loan_termination
        total_interest_paid_contributor = self.loans[1].total_interest_paid

        time_to_loan_termination_diff = time_to_loan_termination_contributor - time_to_loan_termination_all
        total_interest_paid_diff = total_interest_paid_contributor - total_interest_paid_all

        time_impact = time_to_loan_termination_diff / time_to_loan_termination_contributor * 100.0
        interest_impact = total_interest_paid_diff / total_interest_paid_contributor * 100.0

        return time_to_loan_termination_diff, total_interest_paid_diff, time_impact, interest_impact
