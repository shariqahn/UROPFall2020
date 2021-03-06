import gym
import gym_foo
import gym_slider
import numpy as np
import torch
import pickle

from cheetah import HalfCheetah
from mountain_car import ContinuousMountainCarPopulationEnv

from approaches.random_policy import RandomPolicyApproach
from approaches.q_learning import SingleTaskQLearningApproach, MultiTaskQLearningApproach, SingleTaskAugmentedQLearningApproach, MultiTaskAugmentedQLearningApproach
from approaches.dqn import MultiTaskAugmentedOracle, SingleTaskDQN, MultiTaskDQN, SingleTaskAugmentedDQN, MultiTaskAugmentedDQN, MultiTaskDQNOneQuery, MultiTaskDQNTwoQuery
from approaches.ddpg import SingleTaskDDPG, MultiTaskDDPG, MultiTaskDDPGAugmentedOracle, MultiTaskDDPGQuery

num_tasks = 35
overall_steps = 4000*num_tasks
eval_interval = 10
num_seeds = 5
seed_index = 0
def test_single_approach(approach, rng, total_num_tasks=num_tasks):
    results = []
    # task = gym.make('foo-v0')
    # task = gym.make('slider-v0')
    task = HalfCheetah()
    # task = ContinuousMountainCarPopulationEnv()
    approach = approach(task.action_space, task.observation_space, rng)

    results = run_approach_on_task(approach, task, rng, num_tasks=total_num_tasks)
    return results

def run_approach_on_task(approach, task, rng, num_tasks):
    # Task is a Gym env
    state = task.reset(rng)
    approach.reset(task.reward_function)
    # Result is a list of all rewards seen
    result = []
    actions = []
    # count = 0
    # A list of all the states ever visited
    # all_states = [state]
    results = [] # includes e-greedy results
    differences = []
    targets = [task.target]
    eval_results = [] # no e-greedy
    step_count = 0
    max_steps = 1000
    overall_step_count = 0
    while overall_step_count < overall_steps:
    # while len(results) < num_tasks:
        if len(results) % eval_interval == 0:
            action = approach.get_action(state, True)
        else:
            action = approach.get_action(state)
        actions.append(action)
        next_state, reward, done, _ = task.step(action)
        step_count += 1
        overall_step_count += 1
        result.append(reward)
        # all_states.append(next_state)
        # Tell the approach about the transition (for learning)
        approach.observe(state, action, next_state, reward, done)
        if not done:
            done = step_count == max_steps
        
        state = next_state
        if done:
            state = task.reset(rng)
            approach.reset(task.reward_function)
            targets.append(task.target)
            step_count = 0
            # reset environment without rerandomizing
            # allows agent to learn for longer
            # count += 1
            if len(results) % eval_interval == 0:
                eval_results.append(result)

            if (overall_step_count%4000 == 0) and (seed_index == (num_seeds - 1)):
                approach.log(result, task)

            if len(results) % (eval_interval) == 0:
                # print(result)
                # print(f"Finished trial {len(results)}/{num_tasks} with returns {sum(result)}", end='\r')
                print(f"Finished trial {len(results)} ({overall_step_count} steps) with returns {sum(result)}", end='\r')
            results.append(result)

            result = []
            actions = []
    print()
    return eval_results, differences, targets[:-1]
    # , count
    # , all_states


if __name__ == "__main__":
    for approach in (
        # 'SingleTaskDDPG',
        'MultiTaskDDPG',
        'MultiTaskDDPGAugmentedOracle',
        'MultiTaskDDPGQuery',
        # 'MultiTaskAugmentedOracle',
        # 'MultiTaskDQNOneQuery',
        # 'MultiTaskDQNTwoQuery',
        # 'MultiTaskDQN'
        ):
        print(approach)
    # ('Random Policy', 'Single Task', 'Multitask', 'Single Task with Hacking', 'Multitask with Hacking'):
        file = 'results/'
        # if approach == 'Random Policy':
        #     approach_fn = RandomPolicyApproach
        #     file += 'random.pkl'
        # elif approach == 'Single Task':
        #     approach_fn = SingleTaskQLearningApproach
        #     file += 'single_task.pkl'
        # elif approach == 'Multitask':
        #     approach_fn = MultiTaskQLearningApproach
        #     file += 'multitask.pkl'
        # elif approach == 'Single Task with Hacking':
        #     approach_fn = SingleTaskAugmentedQLearningApproach
        #     file += 'single_task_augmented.pkl'
        # elif approach == 'Multitask with Hacking':
        #     approach_fn = MultiTaskAugmentedQLearningApproach
        #     file += 'multitask_augmented.pkl'
        if approach == 'SingleTaskDQN':
            approach_fn = SingleTaskDQN
            file += 'eval_single_dqn.pkl'
        elif approach == 'MultiTaskDQN':
            approach_fn = MultiTaskDQN
            file += 'eval_multi_dqn.pkl'
        elif approach == 'SingleTaskAugmentedDQN':
            approach_fn = SingleTaskAugmentedDQN
            file += 'eval_single_augmented_dqn.pkl'
        elif approach == 'MultiTaskAugmentedDQN':
            approach_fn = MultiTaskAugmentedDQN
            file += 'eval_multi_augmented_dqn.pkl'
        elif approach == 'MultiTaskAugmentedOracle':
            approach_fn = MultiTaskAugmentedOracle
            file += 'eval_MultiTaskAugmentedOracle.pkl'
        elif approach == 'MultiTaskDQNOneQuery':
            approach_fn = MultiTaskDQNOneQuery
            file += 'eval_multi_augmented_dqn_1_query.pkl'
        elif approach == 'MultiTaskDQNTwoQuery':
            approach_fn = MultiTaskDQNTwoQuery
            file += 'eval_multi_augmented_dqn_2_query.pkl'
        elif approach == 'SingleTaskDDPG':
            approach_fn = SingleTaskDDPG
            file += 'SingleTaskDDPG.pkl'
        elif approach == 'MultiTaskDDPG':
            approach_fn = MultiTaskDDPG
            file += 'MultiTaskDDPG.pkl'
        elif approach == 'MultiTaskDDPGAugmentedOracle':
            approach_fn = MultiTaskDDPGAugmentedOracle
            file += 'MultiTaskDDPGAugmentedOracle.pkl'
        elif approach == 'MultiTaskDDPGQuery':
            approach_fn = MultiTaskDDPGQuery
            file += 'MultiTaskDDPGQuery.pkl'

        final_num_tasks = overall_steps//1000//eval_interval
        results = [0]*final_num_tasks
        # goals = [0]*final_num_tasks 
        
        # state_visits = np.zeros((4, 4))
        for i in range(num_seeds):
            print(f"*** STARTING SEED {i} for approach {approach} ***")
            # if i == 0:
            #     difference = [0]*final_num_tasks #difference bw returns and target velocities
            seed_index = i
            rng = np.random.RandomState(i)
            torch.manual_seed(i)
            
            rewards, scores, targets = test_single_approach(approach_fn, rng)
            print(final_num_tasks == len(rewards))

            for j in range(final_num_tasks):
                episode_return = sum(rewards[j])
                results[j] += episode_return/num_seeds

                # goals[j] += current[j][1]/25.0
                # for s in current[j][2]:
                #     r, c = eval(s)
                #     state_visits[r, c] += 1./25.0

        pickle.dump([rewards, scores, targets, results], open(file, "wb"))

