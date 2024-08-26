# app/services/simulation_state.py

# Global variable to track simulation status
simulation_status = False

total_requests = 0
successful_requests = 0
failed_requests = 0
def set_simulation_status(status, totalreq, successfulreq, failedreq ):
    global simulation_status, total_requests, successful_requests, failed_requests

#    print('I am in this simulation state file set_simulation_status function', simulation_status)
    simulation_status = status
    total_requests = totalreq
    successful_requests = successfulreq
    failed_requests = failedreq

def get_simulation_status():
#    print('I am in this simulation state file', simulation_status)
    return simulation_status, total_requests, successful_requests, failed_requests
