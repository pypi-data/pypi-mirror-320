# Time Measure

This package implements a simple context manager ```RuntimeMeter``` to measure the time taken by a block of code, that only add one line of code per section to measure.

```python	
with RuntimeMeter("training"):
    train()

with RuntimeMeter("evaluation"):
    evaluate()
```

## Installation

```bash
pip install tmeasure
```

Or install from source:

```bash
git clone git@github.com:tboulet/PythonTimeMeasure.git
cd PythonTimeMeasure
pip install .
```

## Usage

An example also available in ```example.py``` is given below. This run two functions ```foo``` and ```bar``` three times each and measure the cumulative time taken by each function and the total time taken by the block of code.

```python
import time
from tmeasure import RuntimeMeter

def foo():
    time.sleep(0.1)

def bar():
    time.sleep(0.2)

for _ in range(3):
    with RuntimeMeter("foo function"):
        foo()
    with RuntimeMeter("bar function"):
        bar()

print(RuntimeMeter.get_stage_runtime("foo function"))
print(RuntimeMeter.get_stage_runtime("bar function"))
print(RuntimeMeter.get_stage_runtime("total"))
```

Output :

```
0.3361208438873291
0.6190340518951416
0.9551548957824707
```

To run the example, clone the project and run:

```bash
python example.py
```

## Advanced Usage

The following methods are available :

- Cumulative time : ```RuntimeMeter.get_stage_runtime(stage_name)``` : Get the cumulative time taken by a stage. A variant ```RuntimeMeter.get_runtimes()``` returns a dictionary mapping stage names to their cumulative time.
- Total cumulative time : ```RuntimeMeter.get_total_runtime()``` : Get the total cumulative time taken by all stages. ```RuntimeMeter.get_stage_runtime("total")``` is equivalent to this method.
- Average time : ```RuntimeMeter.get_averaged_stage_runtime(stage_name)``` : Get the average time taken by a stage. If the stage has never been run, it returns 0 by design choice. A variant ```RuntimeMeter.get_averaged_runtimes()``` returns a dictionary mapping stage names to their average time.
- Last measured time : ```RuntimeMeter.get_last_stage_runtime(stage_name)``` : Get the last measured time taken by a stage. If the stage has never been run, it returns None. A variant ```RuntimeMeter.get_last_runtimes()``` returns a dictionary mapping stage names to their last measured time.

## Use cases

This has 2 main use cases :
- Measure the time taken by each part of a loop for informative logging and identify bottlenecks. You may for example apply this to measure the training phase, the evaluation phase, the data loading phase, etc.
- Accessing the total cumulative time of a specific phase(s), which you can then use as an x-axis value in a graph. For example, what may be important in a benchmark can be the curve of any performance metric as a function of the time taken by the training phase.

An example is given in the following hidden section on a interaction agent-environment loop. I measure :

- env reset time
- env render time
- agent act time
- env step time
- env render time
- agent update time

And I do that for both mode "train" and "eval". I can then compare the time taken by each part of the loop in both modes and identify bottlenecks.

<details>
  <summary>Click to expand!</summary>

```python
while (
        episode_train < n_max_episodes_training
        and total_steps_train < n_max_steps_training
    ):
        # Set the settings whether we are in eval mode or not
        if eval_frequency_episode is not None and (episode_train + episode_eval) % eval_frequency_episode == 0:
            is_eval = True
            mode = "eval"
            render_config = render_config_eval
        else:
            is_eval = False
            mode = "train"
            render_config = render_config_train

        # Reset the environment
        with RuntimeMeter(f"{mode}/env reset") as rm:
            state, info = env.reset(seed=seed)
            available_actions = env.get_available_actions(state=state)
            done = False
            episodic_reward = 0
            step = 0

        # Render the environment
        with RuntimeMeter(f"{mode}/env render") as rm:
            try_render(
                env=env,
                episode=episode_eval if is_eval else episode_train,
                step=step,
                render_config=render_config,
                done=done,
            )

        # Play one episode
        while not done and total_steps_train < n_max_steps_training:
            with RuntimeMeter(f"{mode}/agent act") as rm:

                
                action = algo.act(
                    state=state,
                    available_actions=available_actions,
                    is_eval=is_eval,
                )


            with RuntimeMeter(f"{mode}/env step") as rm:
                next_state, reward, is_trunc, done, info = env.step(action)
                next_available_actions = env.get_available_actions(state=next_state)
                #print(next_available_actions)
                episodic_reward += reward

            with RuntimeMeter(f"{mode}/env render") as rm:
                try_render(
                    env=env,
                    episode=episode_eval if is_eval else episode_train,
                    step=step,
                    render_config=render_config,
                    done=done,
                )

            if not is_eval:
                with RuntimeMeter(f"{mode}/agent update") as rm:

                    metrics_from_algo = algo.update(
                        state, action, reward, next_state, done
                    )


            # Update the variables
            state = next_state
            available_actions = next_available_actions
            step += 1
            if is_eval:
                total_steps_eval += 1
            else:
                total_steps_train += 1

            # Logging
            your_logger.log(
                {"episodic_reward": episodic_reward}, 
                step = RuntimeMeter.get_total_runtime(),
                )
```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

