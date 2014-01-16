
def add_username_segment():
    import os
    if powerline.args.shell == 'bash':
        user_prompt = ' \\u '
    elif powerline.args.shell == 'zsh':
        user_prompt = ' %n '
    else:
        user_prompt = ' %s ' % os.getenv('USER')

    if os.geteuid() == 0:
        powerline.append(user_prompt, Color.ROOT_BG, Color.ROOT_FG)
    else:
        powerline.append(user_prompt, Color.USERNAME_FG, Color.USERNAME_BG)

add_username_segment()
