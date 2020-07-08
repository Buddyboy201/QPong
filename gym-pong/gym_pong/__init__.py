from gym.envs.registration import register

register(id='unrendered_pong-v0',
         entry_point='gym_pong.envs:Unrendered',
         )

register(id='rendered_pong-v0',
         entry_point='gym_pong.envs:RenderedPongEnvRendered',
         )