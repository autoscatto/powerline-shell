import re
import subprocess
import sys

def cecco():      
    # change those symbols to whatever you prefer
    symbols = {'ahead of': '↑·', 'behind': '↓·', 'prehash':':'}

    from subprocess import Popen, PIPE

    import sys
    gitsym = Popen(['git', 'symbolic-ref', 'HEAD'], stdout=PIPE, stderr=PIPE)
    branch, error = gitsym.communicate()

    error_string = error.decode('utf-8')

    if 'fatal: Not a git repository' in error_string:
            return False

    branch = branch.decode('utf-8').strip()[11:]

    res, err = Popen(['git','diff','--name-status'], stdout=PIPE, stderr=PIPE).communicate()
    err_string = err.decode('utf-8')

    if 'fatal' in err_string:
            return False

    changed_files = [namestat[0] for namestat in res.splitlines()]
    staged_files = [namestat[0] for namestat in Popen(['git','diff', '--staged','--name-status'], stdout=PIPE).communicate()[0].splitlines()]
    nb_changed = len(changed_files) - changed_files.count('U')
    nb_U = staged_files.count('U')
    nb_staged = len(staged_files) - nb_U
    staged = str(nb_staged)
    conflicts = str(nb_U)
    changed = str(nb_changed)
    status_lines = Popen(['git','status','-s','-uall'],stdout=PIPE).communicate()[0].splitlines()
    untracked_lines = [a for a in status_lines if a.startswith("??")]
    nb_untracked = len(untracked_lines)
    untracked = str(nb_untracked)
    if not nb_changed and not nb_staged and not nb_U and not nb_untracked:
            clean = '1'
    else:
            clean = '0'

    remote = ''

    tag, tag_error = Popen(['git', 'describe', '--exact-match'], stdout=PIPE, stderr=PIPE).communicate()

    if not branch: # not on any branch
            if tag: # if we are on a tag, print the tag's name
                    branch = tag
            else:
                    branch = symbols['prehash']+ Popen(['git','rev-parse','--short','HEAD'], stdout=PIPE).communicate()[0][:-1]
    else:
            remote_name = Popen(['git','config','branch.%s.remote' % branch], stdout=PIPE).communicate()[0].strip()
            if remote_name:
                    merge_name = Popen(['git','config','branch.%s.merge' % branch], stdout=PIPE).communicate()[0].strip()
            else:
                    remote_name = "origin"
                    merge_name = "refs/heads/%s" % branch

            if remote_name == '.': # local
                    remote_ref = merge_name
            else:
                    remote_ref = 'refs/remotes/%s/%s' % (remote_name, merge_name[11:])
            revgit = Popen(['git', 'rev-list', '--left-right', '%s...HEAD' % remote_ref],stdout=PIPE, stderr=PIPE)
            revlist = revgit.communicate()[0]
            if revgit.poll(): # fallback to local
                    revlist = Popen(['git', 'rev-list', '--left-right', '%s...HEAD' % merge_name],stdout=PIPE, stderr=PIPE).communicate()[0]
            behead = revlist.splitlines()
            ahead = len([x for x in behead if x[0]=='>'])
            behind = len(behead) - ahead
            if behind:
                    remote += '%s%s' % (symbols['behind'], behind)
            if ahead:
                    remote += '%s%s' % (symbols['ahead of'], ahead)

    if remote == "":
            remote = '.'
            
    return [str(branch), str(remote), staged, conflicts, changed, untracked, clean]



def add_git_segment():

    resu = cecco()
    bg = Color.REPO_CLEAN_BG
    fg = Color.REPO_CLEAN_FG
    gg = Color.GIT_BG
    if resu is not False:
        #branch remote, staged, conflicts, changed, untracked, clean
        powerline.append(u' %s' % resu[0], Color.GIT_BRANCH, bg)
        if resu[2] != '0':
           powerline.append(u'●%s' % resu[2], Color.GIT_STAGED, gg)
        if resu[3] != '0':
           powerline.append(u'✖%s' % resu[3], Color.GIT_CONFLI, gg)
        if resu[4] != '0':
           powerline.append(u'✚%s' % resu[4], Color.GIT_CHANGE, gg)
        if resu[5] != '0':
           powerline.append(u'…%s' % resu[5], Color.GIT_UNTRAC, gg)   
        if resu[6] == 1:
           powerline.append(u'✔', Color.GIT_CLEAN, gg)   
           

try:
    add_git_segment()
except OSError:
    pass
except subprocess.CalledProcessError:
    pass
