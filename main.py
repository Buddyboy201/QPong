from gym_pong.envs.pong_env import PongEnvUnrendered, PongEnvRendered
import gym
from stable_baselines import DQN
from stable_baselines.deepq.policies import LnMlpPolicy, MlpPolicy

env = PongEnvUnrendered()
#done = False
#state = env.reset(True)
#while not done:
#    action = 1
#    state, reward, done, _ = env.step(action)
#    env.render()
#    print(state, reward)


def episodes_to_timesteps(eps):
    return eps*3530



id = 6
#model = DQN(LnMlpPolicy, env, prioritized_replay=True, verbose=1)
#print(model)
#model.learn(total_timesteps=episodes_to_timesteps(350), log_interval=25)
#model.save("test_{}".format(id))

model = DQN.load("test_{}".format(id))
print(model)

env = PongEnvRendered()
for i in range(100):
    obs = env.reset(True)
    done = False
    while not done:
        action, _states = model.predict(obs)
        #print(_states)
        obs, rewards, _, info = env.step(action)
        print(obs)
        env.render()