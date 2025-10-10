"""
Sort jobs in decreasing order of profit
For each job:
    For slot = min(total slots, job.deadline) downto 1:
        If slot is empty:
            Assign job to slot
            Add job.profit to total profit
            Break

"""
