# 🤖 RLHeist

RLHeist is a reinforcement learning project where agents are trained to perform a "heist" in a 2D environment. The project uses `pygame` for graphics and `torch` with `ray[rllib]` for training the agents in a multi-agent setting.

-----

## 🚀 Getting Started

To get the project running locally, follow these steps:

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    ```

2.  **Navigate to the project directory:**

    ```bash
    cd RLHeist
    ```

3.  **Install dependencies:**

    This project uses Python. You can install all the required libraries using the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

-----

## 🎮 How to Use

### Training the Agents

To train the reinforcement learning agents, run the `train_agents.py` script:

```bash
python train_agents.py
```

### Testing the Agents

To test the trained agents and see them in action, run the `test_agents.py` script:

```bash
python test_agents.py
```

-----

## 🛠️ Tech Stack

  * **Language:** Python
  * **Game Engine / Graphics:** `pygame`
  * **Reinforcement Learning:**
      * **Framework:** `ray[rllib]`
      * **Deep Learning Library:** `torch`
      * **Environment Toolkit:** `gymnasium`
      * **Multi-Agent Environments:** `pettingzoo`
  * **Core Components:**
      * `rlheist_env.py`: The main environment for the heist game.
      * `train_agents.py`: Script for training the RL agents.
      * `test_agents.py`: Script for testing and visualizing the trained agents.
      * `graphics.py`: Handles the graphics and rendering of the game.
      * `collision_handler.py`: Manages collision detection within the game.
      * `light_ray.py`: Implements lighting and vision for the agents.
  * **Data & Visualization:**
      * `numpy`
      * `pandas`
      * `tensorboard` and `tensorboardX` for logging and visualization.

-----

## 📸 Screenshots

*Coming soon...*
