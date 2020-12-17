from algorithms.Loan import Loan
from algorithms.LoanPortfolio import LoanPortfolio
import pandas as pd

class LoanImpacts:
    """ Contributor Impacts to Loan class
    """

    def __init__(self, principal, rate, payment, extra_payment, contributions): 
        # each input is a list: 
        self.principal = principal # principal = [principal_loan1, principal_loan2]
        self.rate = rate
        self.payment = payment
        self.extra_payment = extra_payment
        self.contributions = contributions # contributions = [{'A': 20, 'B': 20, 'C': 0}, {'A': 0, 'B': 10, 'C': 30}]
        self.df_impacts = pd.DataFrame(columns=['Index','InterestPaid','Duration','MIInterest%','MIDuration%','MIInterest','MIDuration'])
    def compute_impacts(self):
        # setup a loan portfolio
        loan_portfolio_all = LoanPortfolio()
        loan_portfolio_none = LoanPortfolio()
       
        # loan with all contributions (mi)_all
        #
        for i in range(len(self.principal)):
            loan_all = Loan(principal=self.principal[i], rate=self.rate[i],
                            payment=self.payment[i], extra_payment=self.extra_payment[i] + sum(self.contributions[i].values()))
            loan_all.check_loan_parameters()   
            loan_all.compute_schedule()
            loan_portfolio_all.add_loan(loan_all)
        loan_portfolio_all.aggregate()
        
        # loan with no contributions (mi)_0
        #
        for i in range(len(self.principal)):
            loan_none = Loan(principal=self.principal[i], rate=self.rate[i],
                             payment=self.payment[i], extra_payment=self.extra_payment[i])
            loan_none.check_loan_parameters()
            loan_none.compute_schedule()
            loan_portfolio_none.add_loan(loan_none)
        loan_portfolio_none.aggregate()

        
        micro_impact_interest_paid_all_pct = \
            (loan_portfolio_none.total_interest_paid - loan_portfolio_all.total_interest_paid) / loan_portfolio_all.total_interest_paid
        micro_impact_duration_all_pct = \
            (loan_portfolio_none.time_to_loan_termination - loan_portfolio_all.time_to_loan_termination) / loan_portfolio_all.time_to_loan_termination

        micro_impact_interest_paid_all = loan_portfolio_none.total_interest_paid - loan_portfolio_all.total_interest_paid
        micro_impact_duration_all = loan_portfolio_none.time_to_loan_termination - loan_portfolio_all.time_to_loan_termination


        # micro_impact_interest_paid_all_pct = loan_portfolio_none.total_interest_paid / loan_portfolio_all.total_interest_paid
        # micro_impact_duration_all_pct = loan_portfolio_none.time_to_loan_termination / loan_portfolio_all.time_to_loan_termination

        self.df_impacts.loc[self.df_impacts.shape[0]] = ['ALL', 
                                                         round(loan_portfolio_all.total_interest_paid, 2), 
                                                         loan_portfolio_all.time_to_loan_termination,
                                                         None,
                                                         None,
                                                         None,
                                                         None
                                                         ]
        self.df_impacts.loc[self.df_impacts.shape[0]] = ['None',
                                                         round(loan_portfolio_none.total_interest_paid, 2),
                                                         loan_portfolio_none.time_to_loan_termination,
                                                         round(micro_impact_interest_paid_all_pct, 4),
                                                         round(micro_impact_duration_all_pct, 4),
                                                         round(micro_impact_interest_paid_all, 2),
                                                         round(micro_impact_duration_all, 2),
                                                         ]

        if len(self.contributions[0]) > 1:
            # loan with each contribution (mi)_index
            #
            for j in range(len(self.contributions[0])):
                loan_portfolio_w_index = LoanPortfolio()
    
                for i in range(len(self.contributions)):
                    loan_index = Loan(principal=self.principal[i], rate=self.rate[i], payment=self.payment[i],
                                      extra_payment=self.extra_payment[i] + list(self.contributions[i].values())[j])
                    loan_index.check_loan_parameters()
                    loan_index.compute_schedule()
                    loan_portfolio_w_index.add_loan(loan_index)
                loan_portfolio_w_index.aggregate() 
        
                micro_impact_interest_paid_pct = \
                    (loan_portfolio_w_index.total_interest_paid - loan_portfolio_all.total_interest_paid) / loan_portfolio_all.total_interest_paid
                micro_impact_duration_pct = \
                    (loan_portfolio_w_index.time_to_loan_termination - loan_portfolio_all.time_to_loan_termination) / loan_portfolio_all.time_to_loan_termination
    
                micro_impact_interest_paid = loan_portfolio_w_index.total_interest_paid - loan_portfolio_all.total_interest_paid
                micro_impact_duration = loan_portfolio_w_index.time_to_loan_termination - loan_portfolio_all.time_to_loan_termination
    
                # micro_impact_interest_paid_pct = loan_portfolio_w_index.total_interest_paid / loan_portfolio_all.total_interest_paid
                # micro_impact_duration_pct = loan_portfolio_w_index.time_to_loan_termination / loan_portfolio_all.time_to_loan_termination
    
                self.df_impacts.loc[self.df_impacts.shape[0]] = [list(self.contributions[i])[j],
                                                                 round(loan_portfolio_w_index.total_interest_paid, 2),
                                                                 loan_portfolio_w_index.time_to_loan_termination,
                                                                 round(micro_impact_interest_paid_pct, 4),
                                                                 round(micro_impact_duration_pct, 4),
                                                                 round(micro_impact_interest_paid, 2),
                                                                 round(micro_impact_duration, 2)
                                                                 ]
    

        if len(self.contributions[0]) == 3:
            # loan without each contribution (mi)_index
            #
            for j in range(len(self.contributions[0])):
                loan_portfolio_wo_index = LoanPortfolio()
               
                for i in range(len(self.contributions)):
                    loan_index = Loan(principal=self.principal[i], rate=self.rate[i], payment=self.payment[i],
                                      extra_payment=self.extra_payment[i] + sum(self.contributions[i].values()) - list(self.contributions[i].values())[j])
                    loan_index.check_loan_parameters()
                    loan_index.compute_schedule()
                    loan_portfolio_wo_index.add_loan(loan_index)
                loan_portfolio_wo_index.aggregate() 
        
                micro_impact_interest_paid_pct = \
                    (loan_portfolio_wo_index.total_interest_paid - loan_portfolio_all.total_interest_paid) / loan_portfolio_all.total_interest_paid
                micro_impact_duration_pct = \
                    (loan_portfolio_wo_index.time_to_loan_termination - loan_portfolio_all.time_to_loan_termination) / loan_portfolio_all.time_to_loan_termination

                micro_impact_interest_paid = loan_portfolio_wo_index.total_interest_paid - loan_portfolio_all.total_interest_paid
                micro_impact_duration = loan_portfolio_wo_index.time_to_loan_termination - loan_portfolio_all.time_to_loan_termination
    
                # micro_impact_interest_paid = loan_portfolio_wo_index.total_interest_paid / loan_portfolio_all.total_interest_paid
                # micro_impact_duration = loan_portfolio_wo_index.time_to_loan_termination / loan_portfolio_all.time_to_loan_termination
                index_member = list(self.contributions[i])
                index_member.pop(j)
                self.df_impacts.loc[self.df_impacts.shape[0]] = [' and '.join(index_member),
                                                                 round(loan_portfolio_wo_index.total_interest_paid, 2),
                                                                 loan_portfolio_wo_index.time_to_loan_termination,
                                                                 round(micro_impact_interest_paid_pct, 4),
                                                                 round(micro_impact_duration_pct, 4),
                                                                 round(micro_impact_interest_paid, 2),
                                                                 round(micro_impact_duration, 2)
                                                                 ]

#        self.df_impacts = self.df_impacts.reset_index().drop(labels='index',axis=1)
#        print(self.df_impacts)
        return self.df_impacts