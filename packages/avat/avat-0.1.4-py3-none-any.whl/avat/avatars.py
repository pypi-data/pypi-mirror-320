import requests
import json
from icecream import ic
from .api_request import ApiRequest
from .utils import get_av_headers, get_eval_data, get_avatar_data, get_chat_headers, get_base_url, get_eval_headers
import concurrent.futures
import time

def parse_agent_reply(tested_agent_response):
    # Parse the agent reply from the REST API response
    if "agent_reply" in tested_agent_response.json():
        return tested_agent_response.json()["agent_reply"]
    else:
        raise Exception("No agent_reply in response")
    
class EvalRunner():

    def __init__(self, auth_token, env="cloud"):
        self.auth_token = auth_token
        self.env = env


        self.base_url = get_base_url(env)
        self.evals_url = self.base_url + 'run_msg_eval/'
        self.evals_run_update_url = self.base_url + 'update_eval_run/'
        self.avatar_url = self.base_url + 'chat/'
        self.evals_run_url = self.base_url + 'create_eval_run/'

        self.evals_headers = get_eval_headers(auth_token)
        self.avatar_headers = get_av_headers(auth_token)
        self.chat_headers =  get_chat_headers(auth_token)
        

    def run_chat_evals(self, 
                    custom_eval_questions, 
                    standard_eval_tags, 
                    tested_agent_endpoints,  
                    n_max_turns=2, 
                    n_chats=2, 
                    avatar_id="671e876cb93db3a0c724b1d5", 
                    tested_agent_avatar_mes_key = "avatar_msg", 
                    json_flag=True,
                    eval_every_message=False,
                    agent_response_parser=parse_agent_reply, 
                    start_chat_endpoints=None,
                    start_chat_fields_to_msg=[]
                    ):
        

        
        self.tested_agent_url, self.tested_agent_headers, self.agent_data = tested_agent_endpoints
        ev_run_data = {"n_runs":str(n_chats), "tot_eval_scores": {}, "aggregate_score": "0"}
        evals_run = ApiRequest(self.evals_run_url, self.evals_headers, ev_run_data).post().json()

        run_id = evals_run["eval_run_id"]        
        tot_eval_scores = {}    

        self.tested_agent_avatar_mes_key = tested_agent_avatar_mes_key
        self.n_max_turns = n_max_turns
        self.eval_every_message = eval_every_message
        self.run_id = run_id
        self.custom_eval_questions = custom_eval_questions
        self.standard_eval_tags = standard_eval_tags
        self.avatar_id = avatar_id
        self.json_flag = json_flag
        self.agent_response_parser = agent_response_parser
        self.start_chat_endpoints = start_chat_endpoints
        self.start_chat_fields_to_msg = start_chat_fields_to_msg

        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            avatar_run = [executor.submit(self._run_chat_evals, 
                                        ) for run_n in range(0, n_chats)]
            
            for future in concurrent.futures.as_completed(avatar_run):
                correct_count, tot, eval_scores = future.result()
                
                for ev,score in eval_scores.items():
                    if ev in tot_eval_scores:
                        tot_eval_scores[ev] += score
                    else:
                        tot_eval_scores[ev] = score
        
        
        accuracy_scores, aggregate_score = self.get_tot_eval_scores(tot_eval_scores, n_chats)
        evals_run_response = ApiRequest(self.evals_run_update_url, self.evals_headers, {"run_id": run_id, "tot_eval_scores": accuracy_scores, "aggregate_score": aggregate_score}).post()

    def _run_chat_evals(self,   
                        sleep_time=2,
                        ):

        correct_count = 0
        tot = 0        

        # If the agent need to start the chat with an API call, do it here.
        if self.start_chat_endpoints:
            start_chat_url, start_chat_headers, start_chat_data = self.start_chat_endpoints
            new_chat_session = ApiRequest(start_chat_url, start_chat_headers, start_chat_data).post()
            for api_field in self.start_chat_fields_to_msg:
                self.agent_data[api_field[1]] = new_chat_session.json()[api_field[0]]
        
        av = get_avatar(self.avatar_id, self.auth_token, env=self.env)
        avatar_first_message = av.json()["first_message"]
        self.agent_data[self.tested_agent_avatar_mes_key] = avatar_first_message

        self.agent_data["is_new_chat"] = True
        tested_agent_response = ApiRequest(self.tested_agent_url, self.tested_agent_headers, self.agent_data, json_flag=self.json_flag).post()
        tested_agent_response = self.agent_response_parser(tested_agent_response)
        ic(tested_agent_response)
        
        avatar_data = get_avatar_data(new_chat=True,tested_agent_msg=tested_agent_response, avatar_id=self.avatar_id)
        avatar_response = ApiRequest(self.avatar_url, self.avatar_headers, avatar_data).post()
        avatar_reply = avatar_response.json()["avatar_reply"]
        ic(avatar_reply)

        chat_session_id = avatar_response.json()["chat_session_id"]
        self.agent_data["chat_session_id"] = chat_session_id # to support the dummy agent
        self.agent_data[self.tested_agent_avatar_mes_key] = avatar_reply
        
        if self.eval_every_message:
            evals_response = ApiRequest(self.evals_url, self.evals_headers, get_eval_data(tested_agent_response, chat_session_id, self.custom_eval_questions, self.standard_eval_tags)).post()
            self.compute_score(evals_response)

        for i in range(0, self.n_max_turns):

            time.sleep(sleep_time)
            
            self.agent_data["is_new_chat"] = False
            self.agent_data["chat_session_id"] = chat_session_id
            tested_agent_response = ApiRequest(self.tested_agent_url, self.tested_agent_headers, self.agent_data, json_flag=self.json_flag).post()
            tested_agent_response = self.agent_response_parser(tested_agent_response)
            ic(tested_agent_response)

            avatar_data = get_avatar_data(new_chat=False, chat_session_id=chat_session_id,tested_agent_msg=tested_agent_response, avatar_id =self.avatar_id)
            avatar_response = ApiRequest(self.avatar_url, self.avatar_headers, avatar_data).post()
            avatar_reply = avatar_response.json()["avatar_reply"]
            ic(avatar_reply)
            is_last_avatar_message = avatar_response.json()["is_last_message"]

            self.agent_data[self.tested_agent_avatar_mes_key] = avatar_reply 

            if self.eval_every_message:
                evals_response = ApiRequest(self.evals_url, self.evals_headers, get_eval_data(tested_agent_response, chat_session_id, self.custom_eval_questions, self.standard_eval_tags)).post()
                self.compute_score(evals_response)

            if is_last_avatar_message:
                break


        # Get whole chat
        chat_url = self.base_url + 'get_chat/' + "?chat_session_id=" + chat_session_id
        chat_response = ApiRequest(chat_url, self.chat_headers).get()
        #ic(chat_response.json())
        whole_chat = str(chat_response.json()['previous_conversation'])
        

        # Eval whole chat
        evals_response = ApiRequest(self.evals_url, self.evals_headers, get_eval_data(whole_chat, chat_session_id, self.custom_eval_questions, self.standard_eval_tags)).post()
        evals_run_response = ApiRequest(self.evals_run_update_url, self.evals_headers, {"run_id": self.run_id, "eval_chat_ids": [chat_session_id,]}).post()

        accuracy_count, tot_count, eval_scores = self.compute_score(evals_response, verbose=False)

        correct_count += accuracy_count
        tot += tot_count

        return correct_count, tot, eval_scores

        
                
    def get_tot_eval_scores(self, tot_eval_scores, n_runs, verbose=True):

        accuracy_scores = {}
        aggregate_score = 0

        if verbose: print("Eval Results for " + str(n_runs) + " runs:")
        for ev,score in tot_eval_scores.items():
            acc = round(score / n_runs, 3)
            s_acc = str(acc)
            accuracy_scores[ev] = s_acc
            if verbose: print(ev + ": " + s_acc)
            aggregate_score += acc

        aggregate_score = str(round(aggregate_score / len(tot_eval_scores), 3))

        return accuracy_scores, aggregate_score


    def compute_score(self, evals_response, verbose=False):

        evals_response = evals_response.json()["evals"]

        accuracy_count = 0
        tot_count = 0

        if len(evals_response) == 0:
            return ""
        
        log = "########################### \nMessage to evaluate: \n"
        log += evals_response[0]["msg_to_eval"] + "\n"
        log += "########################### \nEvaluation: \n"

        eval_scores = {}

        for eval in evals_response:

            tot_count += 1
            result = eval["eval_result"]

            score = 0
            if "pass" in result.lower():
                score = 1
                
            accuracy_count += score

            if "eval_question" in eval:
                log += result + ": " + str(eval["eval_question"]) + "\n"
                eval_scores[eval["eval_question"]] = score

            elif "eval_tag" in eval:
                log += result + ": " + str(eval["eval_tag"]) + "\n"
                eval_scores[eval["eval_tag"]] = score

        log += "########################## \nAccuracy: \n"
        log += str(accuracy_count) + "/" + str(tot_count) + "\n"

        if verbose:
            print(log)
        return accuracy_count, tot_count, eval_scores

def get_avatar(avatar_id, auth_token, env="cloud"):

    base_url = get_base_url(env)
    avatar_url = base_url + 'avatars/' + avatar_id
    avatar_headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer ' + auth_token,
    }
    avatar = ApiRequest(avatar_url, avatar_headers).get()
    return avatar

def create_avatar(auth_token, avatar_profile, env="cloud"):

    base_url = get_base_url(env)
    avatar_url = base_url + '/avatars'
    avatar_headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer ' + auth_token,
    }

    avatar_info = ApiRequest(avatar_url, avatar_headers, avatar_profile).post()
    return avatar_info.json()