from typing import Callable, List, Dict, Optional, Set, Tuple
from Classes.Loan import Loan, SplitAllocation


def cut_loans_with_split(
        target_amount: int,
        loans: List[Loan],
        partitioner: Callable[[Loan], str] = lambda x: x.trustPortfolio,
        accumulator: Callable[[Loan], str] = lambda x: x.financeAmount,
        splits: List[Tuple[str, int]] = None,
        splitEvenly: bool = False
        ) -> List[Loan]:
    
    result : List[Loan] = []
    
    # if the defined split is None, then we will create a split for each unique property (which is default to the trustPortfolio)
    if splitEvenly is True:
        unique_splittable_items: Set[str] = {partitioner(loan) for loan in loans}
        splits = [(split, 100 // len(unique_splittable_items)) for split in unique_splittable_items]
        
    # create a dictionary of the splits with the target amount and remaining amount for each split
    splits: Dict[str, SplitAllocation] = {
        name : SplitAllocation(name=name, targetAmount=int(target_amount * percent / 100), remainingAmount=int(target_amount * percent / 100))
        for name, percent in splits
    }
    
    # sort the loans by accumulator in descending order to allocate the largest values first
    loans.sort(key=accumulator, reverse=True)

    # allocate the loans based on what you split them by
    # if the loan is less than or equal to the remaining amount of the split, then allocate the loan to the split
    # an example of this being used could be to split on asset type(you pick this by defining what the split property should be for property_selector ^^^ ), and then fill those splits based on the finance amount
    for loan in loans:
        split_name = partitioner(loan)
        split = splits.get(split_name)
        if split and accumulator(loan) <= split.remainingAmount:
            split.allocations.append(loan)
            split.remainingAmount -= accumulator(loan)
            print(f"Allocated loan ID {loan.loanNumber} of ${accumulator(loan)} for {split.name}. Remaining amount for split: ${split.remainingAmount:.2f}")
            
    for split_name, split in splits.items():
        result.extend(split.allocations)

    print("\n")

    return result

#this one is for when the list of loans doesnt have a split specified
def cut_loans(
        target_amount: int,
        loans: List[Loan],
        accumulator: Callable[[Loan], str] = lambda x: x.financeAmount
        ) -> List[Loan]:
    
    result : List[Loan] = []
    
    # sort the loans by accumulator in descending order to allocate the largest values first
    loans.sort(key=accumulator, reverse=True)

    # allocate the loans until the target amount is reached
    remaining_amount = target_amount
    for loan in loans:
        loan_amount = accumulator(loan)
        if loan_amount <= remaining_amount:
            result.append(loan)
            remaining_amount -= loan_amount
            print(f"Allocated loan ID {loan.loanNumber} of ${loan_amount}. Remaining amount: ${remaining_amount:.2f}")
        if remaining_amount == 0:
            break

    print("\n")

    return result