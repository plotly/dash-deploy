from config import *

from subprocess import call

# https://stackoverflow.com/questions/287871/print-in-terminal-with-colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

DASH_SERVER = raw_input(bcolors.BOLD + "What's the URL of your dash server ? " + bcolors.ENDC)
link_redis = None

print(bcolors.OKBLUE + "The name of your dash app is: "+DASH_APP_NAME + bcolors.ENDC)

print(bcolors.OKBLUE + "Your dash server is: "+DASH_SERVER + bcolors.ENDC)

TRACKED_REPO = DASH_SERVER.replace('.', '-')+'-'+DASH_APP_NAME.replace('.', '-')
print(bcolors.OKBLUE + "The tracked repo is: "+TRACKED_REPO + bcolors.ENDC)

# Change number of workers if needed
while True:
	link_celery = raw_input(bcolors.BOLD + "Do you need to add or change the number of workers for your app? You probably need to do this if you're using celery (Yes/No): " + bcolors.ENDC)
	if link_celery.lower() == "yes":
		workers = raw_input(bcolors.BOLD + bcolors.BOLD + "How many workers does your app need? " + bcolors.ENDC)
		print(bcolors.OKBLUE + 'Running: ssh dokku@'+DASH_SERVER+' ps:scale '+DASH_APP_NAME+' worker='+workers + bcolors.ENDC)
		ps_scale_code = call(['ssh', 'dokku@'+DASH_SERVER, 'ps:scale', DASH_APP_NAME, 'worker='+workers])
		if ps_scale_code == 0:
			print(bcolors.OKGREEN + DASH_APP_NAME+' was scaled to '+workers+' workers' + bcolors.ENDC)
			link_redis = "yes"
			break
		else:
			exit()
	if link_celery.lower() == "no":
		print(bcolors.OKBLUE + "Not changing the number of workers..." + bcolors.ENDC)
		break

# Link to redis if needed
while True:
	if link_redis not in ["yes", "no"]:	
		link_redis = raw_input(bcolors.BOLD + "Do you need a Redis instance for your app? (Yes/No): " + bcolors.ENDC).lower()
	if link_redis == "yes":
		while True:
			existing_redis = raw_input(bcolors.BOLD + "Do you want to link an existing Redis instance? (Yes/No): " + bcolors.ENDC)
			if existing_redis.lower() == "yes":
				redis_service = raw_input(bcolors.BOLD + "Please type the name of the existing Redis Service you want to link: " + bcolors.ENDC)
				break
			if existing_redis.lower() == "no":
				redis_service = raw_input(bcolors.BOLD + "Please type the name of the new Redis Service you want to link: " + bcolors.ENDC)
				print(bcolors.OKBLUE + 'Running: ssh dokku@'+DASH_SERVER+' redis:create '+redis_service + bcolors.ENDC)
				redis_create_code = call(['ssh', 'dokku@'+DASH_SERVER, 'redis:create', redis_service])
				if redis_create_code == 0:
					print(bcolors.OKGREEN + 'Redis service '+redis_service+' was created' + bcolors.ENDC)
					break
				else:
					exit()
		print(bcolors.OKBLUE + 'Running: ssh dokku@'+DASH_SERVER+' redis:link '+redis_service+' '+DASH_APP_NAME + bcolors.ENDC)
		redis_link_code = call(['ssh', 'dokku@'+DASH_SERVER, 'redis:link', redis_service, DASH_APP_NAME])
		if redis_link_code in [0, 1]:
			print(bcolors.OKGREEN + 'Redis service '+redis_service+' was linked to dash app '+DASH_APP_NAME + bcolors.ENDC)
			break
		else:
			exit()
	if link_redis == "no":
		print(bcolors.OKBLUE + "Not linking Redis..." + bcolors.ENDC)
		break

# Git remote add tracked-repo
print(bcolors.OKBLUE + 'Running: git remote add '+TRACKED_REPO+' dokku@'+DASH_SERVER+':'+DASH_APP_NAME + bcolors.ENDC)
git_remote_add_code = call(['git', 'remote', 'add', TRACKED_REPO, 'dokku@'+DASH_SERVER+':'+DASH_APP_NAME])
if git_remote_add_code == 0:
	print(bcolors.OKGREEN + 'New remote tracked repo added, carrying on...' + bcolors.ENDC)
elif git_remote_add_code == 128:
	print(bcolors.OKGREEN + 'Remote tracked repo exists already, carrying on using it...' + bcolors.ENDC)
else:
	exit()

# Git add
while True:
	git_add = raw_input(bcolors.BOLD + "Do you want to add all your changes to git? (Yes/No): " + bcolors.ENDC)
	if git_add.lower() == "yes":
		while True:
			call(['git', 'status'])
			git_status = raw_input(bcolors.BOLD + "These are the changes that are gonna be added, you wanna continue? (Yes/No): " + bcolors.ENDC).lower()
			if git_status == "yes":
				print(bcolors.OKBLUE + 'Running: git add .' + bcolors.ENDC)
				git_add_code = call(['git', 'add', '.'])
				if git_add_code == 0:
					print(bcolors.OKGREEN + 'Changes staged with git' + bcolors.ENDC)
					break
				else:
					exit()
			if git_status == "no":
				print(bcolors.OKBLUE + "Exiting..." + bcolors.ENDC)
				exit()
		break
	if git_add.lower() == "no":
		print("Exiting..." + bcolors.ENDC)
		exit()

# Git commit
git_commit_message = raw_input(bcolors.BOLD + "Enter a message for your commit: " + bcolors.ENDC)
print(bcolors.OKBLUE + 'Running: git commit -m "'+git_commit_message+'"' + bcolors.ENDC)
git_commit_code = call(['git', 'commit', '-m', '"'+git_commit_message+'"'])
if git_commit_code == 0:
	print(bcolors.OKGREEN + 'Changes commited with git' + bcolors.ENDC)
else:
	exit()

# Git push
while True:
	deploy = raw_input(bcolors.BOLD + "Are you on the branch master? (Yes/No): " + bcolors.ENDC).lower()
	if deploy == "yes":
		print(bcolors.OKBLUE + 'Running: git push '+TRACKED_REPO+' master' + bcolors.ENDC)
		git_push_code = call(['git', 'push', TRACKED_REPO, 'master'])
		if git_push_code == 0:
			print(bcolors.OKGREEN + 'Your app was deployed successfully' + bcolors.ENDC)
			break
		else:
			exit()
	if deploy == "no":
		git_branch = raw_input(bcolors.BOLD + "Enter the name of your branch: " + bcolors.ENDC)
		print(bcolors.OKBLUE + 'Running: git push '+TRACKED_REPO+' '+git_branch+':master' + bcolors.ENDC)
		git_push_code = call(['git', 'push', TRACKED_REPO, git_branch+':master'])
		if git_push_code == 0:
			print(bcolors.OKGREEN + 'Your app was deployed successfully' + bcolors.ENDC)
			break
		else:
			exit()

print(bcolors.HEADER + 'Done.' + bcolors.ENDC)