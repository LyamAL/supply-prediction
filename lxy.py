import pandas
import seaborn as sns
from pylab import *

def linefor3():
    df2 = pandas.read_csv(
        '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/cfaba1663508ae208088ed908ede3fd3/File/results/experiment_dqn_ablation_no_hist.csv',
        engine='python', skip_blank_lines=True)
    df1 = pandas.read_csv(
        '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/cfaba1663508ae208088ed908ede3fd3/File/results/experiment_dqn_ablation_nomap.csv',
        engine='python', skip_blank_lines=True)
    df3 = pandas.read_csv(
        '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/cfaba1663508ae208088ed908ede3fd3/File/results/experiment_DQN_small_scale_final.csv',
        engine='python', skip_blank_lines=True)
    df1 = df1[['training_iteration', 'episode_reward_mean']]
    df2 = df2[['training_iteration', 'episode_reward_mean']]
    df3 = df3[['training_iteration', 'episode_reward_mean']]

    plt.rcParams["font.sans-serif"] = ["Times New Roman"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.rcParams.update({'font.size': 30})
    plt.figure(figsize=(10, 10))

    ax = sns.lineplot(data=df1, x='training_iteration', y='episode_reward_mean')
    sns.lineplot(data=df2, x='training_iteration', y='episode_reward_mean', ax=ax)
    sns.lineplot(data=df3, x='training_iteration', y='episode_reward_mean', ax=ax)
    ax.set_ylabel('mean_reward')
    ax.set_xlabel('iteration')
    plt.tight_layout()
    # plt.savefig(f'pngs/梁星元/dqn_ablation.png')
    plt.show()


def linefor1(path):
    df = pandas.read_csv(
        path,
        engine='python', skip_blank_lines=True)
    df = df[['training_iteration', 'episode_reward_mean']]

    plt.rcParams["font.sans-serif"] = ["Times New Roman"]  # 正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    plt.rcParams.update({'font.size': 30})
    plt.figure(figsize=(10, 10))

    plt.xlabel('iteration')
    plt.ylabel('Mean_reward')
    sns.lineplot(data=df, x='training_iteration', y='episode_reward_mean')
    plt.tight_layout()
    # plt.savefig(f'pngs/梁星元/{path[-12:-4]}.png')
    plt.show()


if __name__ == '__main__':
    linefor3()
    linefor1(
        '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/cfaba1663508ae208088ed908ede3fd3/File/results/experiment_A2C_car2.csv')
    linefor1(
        '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/cfaba1663508ae208088ed908ede3fd3/File/results/experiment_A2C_car3.csv')
    linefor1(
        '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/cfaba1663508ae208088ed908ede3fd3/File/results/experiment_A2C_car4.csv')
    linefor1(
        '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/cfaba1663508ae208088ed908ede3fd3/File/results/experiment_dqn_car3.csv')
    linefor1(
        '/Users/lyam/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/25616cbae1ede48acaba0badcbc8039c/Message/MessageTemp/cfaba1663508ae208088ed908ede3fd3/File/results/experiment_dqn_car4.csv')
