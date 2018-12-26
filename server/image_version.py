import argparse
import json
import pprint
import subprocess
import os
import re


def get_latest_git_commit_hash():
    """Retrieve the first part of the latest git log commit hash

    :return:
    """
    cmd = "git log -1 --pretty=%h"
    output = run_cmd(cmd)[0]
    return output.split()[0]


def clean_controller_images(version, file_mode):
    """Clean up the Docker images nginx-uwsgi-falcon-server:{tag} and syangnub/nginx-uwsgi-falcon-server:{tag}

    :param version:
    :param file_mode:
    :return:
    """
    msg = "\nCleaning up controller image with tag '{}'...\n".format(version)
    print(msg)
    with open("image.log", file_mode) as f:
        f.write(msg)
        cmd = "docker rmi -f nginx-uwsgi-falcon-server:{} syangnub/nginx-uwsgi-falcon-server:{}".format(version, version)
        run_cmd(cmd, json_load=True, out=f)


def make_controller(version, file_mode):
    """Build Docker images nginx-uwsgi-falcon-server:{tag} and syangnub/nginx-uwsgi-falcon-server:{tag}

    :param version:
    :param file_mode:
    :return:
    """
    msg = "\nBuilding controller image with tag '{}'...\n".format(version)
    print(msg)
    with open("image.log", file_mode) as f:
        f.write(msg)
        cmd = "docker build . -t nginx-uwsgi-falcon-server:{} -t syangnub/nginx-uwsgi-falcon-server:{}".format(version, version)
        run_cmd(cmd, json_load=True, out=f)


def push_image(version, file_mode):
    """Push Docker image syangnub/nginx-uwsgi-falcon-server:{tag} to Docker Hub

    :param version:
    :param file_mode:
    :return:
    """
    msg = "\nPushing docker image with tag '{}'...\n".format(version)
    print(msg)
    with open("image.log", file_mode) as f:
        f.write(msg)
        cmd = "docker push syangnub/nginx-uwsgi-falcon-server:{}".format(version)
        run_cmd(cmd, json_load=True, out=f)


def valid_version_format(version):
    """Return bool if version is of format X.Y.Z where X, Y, and Z are digits.

    :param version:
    :return:
    """
    return re.match(r'\d+(\.\d+)*$', version) is not None


def get_version(version_file_name="VERSION"):
    """Retrieve the current version from the file VERSION.

    :param version_file_name:
    :return:
    """
    with open(version_file_name) as f:
        version = f.readline()
        if not valid_version_format(version):
            return

    return version


def image_tag_exists(tag):
    cmd = "docker pull syangnub/nginx-uwsgi-falcon-server:{}".format(tag)
    output, error = run_cmd(cmd, json_load=True)
    return not error


def fetch_latest_hub_version(version_file_name="VERSION"):
    cmd = "docker pull syangnub/nginx-uwsgi-falcon-server:latest"
    run_cmd(cmd, json_load=True)

    cmd = "docker run syangnub/nginx-uwsgi-falcon-server:latest cat {}".format(version_file_name)
    output, error = run_cmd(cmd, json_load=True)
    return output.split()[0] if output else None


def update_version_file(version, version_file_name="VERSION", mode=None):
    """Update file VERSION with the version input as an argument.

    :param version:
    :param version_file_name:
    :return:
    """
    if not valid_version_format(version) and mode != "test":
        raise ValueError("Version {} is not valid. Must be \d.\d.\d format.".format(version))

    with open(version_file_name, "w") as f:
        f.write(version)
        return


def calculate_new_version(mode, version):
    """Calculate the new version based on the mode.

    Version should be of format X.Y.Z where X, Y, and Z are digits.
    Major will increment X by 1.
    Minor will increment Y by 1.
    Patch will increment Z by 1.

    :param mode: (str) major, minor, or patch
    :param version:
    :return:
    """
    if not valid_version_format(version):
        raise ValueError("Version {} is not valid. Must be \d.\d.\d format.".format(version))

    version_parts = version.split('.')
    if mode == "major":
        new_version = "{}.0.0".format(int(version_parts[0]) + 1)
    elif mode == "minor":
        new_version = "{}.{}.0".format(version_parts[0], int(version_parts[1]) + 1)
    elif mode == "patch":
        new_version = "{}.{}.{}".format(version_parts[0], version_parts[1], int(version_parts[2]) + 1)
    else:
        raise ValueError("Unknown version update mode: {}. Must be major, minor, or patch.".format(mode))

    return new_version


def get_confirmation(msg):
    answer = raw_input(msg)
    if answer.lower() not in ["y", "yes", "ye"]:
        print("\nStopping update due to non-confirmation input.")
        exit(1)


def run_cmd(cmd, params=None, verbose=False, json_load=False, out=subprocess.PIPE, err=subprocess.PIPE):
    if isinstance(cmd, str):
        cmd = cmd.split()
        if params:
            cmd += params
    output, error = _mys(cmd, verbose=verbose, out=out, err=err)

    if verbose and output:
        print("\nOutput:")
        print(output)

    if verbose and error:
        print("\nError:")
        print(error)

    if json_load:
        output = json.loads(json.dumps(output)) if output else None
    else:
        output = output if output else None

    if verbose:
        pprint.pprint(output, indent=4)

    return output, error


def _mys(cmd, env=None, log_errors=False, dry_run=False, out=subprocess.PIPE, err=subprocess.PIPE, verbose=True):
    """

    :param cmd: (list/str) Command can be either. shell=True is used when cmd is a str
    :param env:
    :param log_errors: (bool)
    :param dry_run: (bool) Print command, but do not execute
    :param out:
    :param err:
    :return:
    """
    # If cmd is a lists, then call it as arguments without a shell
    # Otherwise, assume it is a string and needs shell=True
    if verbose:
        print("Calling command: {}".format(cmd))
    shell = True
    if isinstance(cmd, list):
        shell = False

    # Update environment if need be
    r = os.environ.copy()
    if env:
        r.update(env)

    # If dry run, print command and exit method
    if dry_run:
        msg = "Running: {}".format([cmd, "shell={}".format(shell)])
        if env:
            msg = "Running: {}".format([cmd, "env={}".format(r), "shell=".format(shell)])
        if verbose:
            print(msg)
        return

    # Execute command using subprocess
    if env:
        proc = subprocess.Popen(cmd, env=r, shell=shell, stdout=out, stderr=err)
    else:
        proc = subprocess.Popen(cmd, shell=shell, stdout=out, stderr=err)

    (output, error) = proc.communicate()

    if log_errors and error and verbose:
        print("Process returned error {}".format(error))
    if proc.returncode < 0 and verbose:
        print("Got negative return code, hit resource limit on subprocess")
        print("Process returned error {}".format(error))
        print("Got negative return code, hit resource limit on subprocess")
    if proc.returncode != 0 and verbose:
        print("Process returned error {}".format(error))
        print("Got Error {} calling command '{}'".format(proc.returncode, cmd))

    # reap zombies
    try:
        os.waitpid(-1, os.WNOHANG)
    except:
        pass

    return output, error


def build_and_push_latest(version, mode, dry_run, yes):
    """This method must be called after build_and_push_version() or build_and_push_mode().

    :param version:
    :param mode:
    :param dry_run:
    :param yes:
    :return:
    """
    if mode == "test":
        print("\nMode cannot be 'test' when build/push latest.")
        exit(1)

    if not version:
        version = get_version()

    if mode:
        docker_hub_version = fetch_latest_hub_version()

        if not docker_hub_version:
            print("\nNo previous Docker Hub syangnub/nginx-uwsgi-falcon-server version found.")
        else:
            print("\nDocker hub's syangnub/nginx-uwsgi-falcon-server:latest is at version {}. "
                  "You're trying to change to version {}.".format(docker_hub_version, version))

        if not yes:
            msg = "Would you like to set the Docker Hub's syangnub/nginx-uwsgi-falcon-server:latest version to {}?" \
                  " (Y/n) ".format(version)
            get_confirmation(msg)

    clean_controller_images("latest", 'a+')
    update_version_file(version)
    make_controller("latest", 'a+')

    if not dry_run:
        push_image("latest", 'a+')

    return version


def build_and_push_version(version, dry_run):
    """

    Change an existing image with same version tag.

    Can be used to change latest tag image to different version.
        For example, if syangnub/nginx-uwsgi-falcon-server:latest is at version 1.0.1 and you want to skip
        to 3.0.0, then use this function by specifying version as 3.0.0. The VERSION file
        will also be updated to 3.0.0.

    :param version:
    :param dry_run:
    :return:
    """

    # Grant permission to update and push version even if one exists
    if image_tag_exists(version):
        msg = "\nUpdating version {} when version exists in Docker Hub. Would you like to continue? (Y/n) ".format(version)
        get_confirmation(msg)

    clean_controller_images(version, 'a+')

    # Update version file for specific docker image but change version back after building image
    old_version = get_version()
    update_version_file(version)
    # build the docker image with tagged versioning
    make_controller(version, 'a+')
    update_version_file(old_version)

    # push up docker image
    if not dry_run:
        push_image(version, 'a+')

    return version


def build_and_push_mode(mode, dry_run):
    """Build controller docker image and push controller docker image.

    If version is not specified, then the version in VERSION file will be updated based on the mode.
    If version is specified, then the specific docker image with the specified version tag will be updated only.
        The latest image tag will not be updated.

    If mode == 'test', then syangnub/nginx-uwsgi-falcon-server:latest will NOT be updated.

    :param mode: (str) major, minor, patch, test
    :param dry_run: (bool)
    :return: (str) version
    """
    # make pylib
    # make_pylib('w')

    new_version = ""
    old_version = get_version()
    # get new version and update version file
    if mode in ['major', 'minor', 'patch']:
        # open up versioning
        new_version = calculate_new_version(mode, old_version)

        if image_tag_exists(new_version):
            print("\nTrying to build and push an image with version tag {}, but this tag already exists.".format(new_version))
            msg = "Would you like to continue and overwrite Docker Hub image? (Y/n) ".format(new_version)
            get_confirmation(msg)

    elif mode == 'test':
        # Use git hash for the build and push
        new_version = get_latest_git_commit_hash()

    # Update version file for specific docker image but change version back after building image
    update_version_file(new_version, mode=mode)
    # build the docker image with tagged versioning
    make_controller(new_version, 'a+')
    update_version_file(old_version, mode=mode)

    # push up docker image
    if not dry_run:
        push_image(new_version, 'a+')

    return new_version


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A tool that helps build and push syangnub/nginx-uwsgi-falcon-server image "
                                                 "versions/tags.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--mode", dest='mode', type=str, choices={'major', 'minor', 'patch', 'test'},
                        help="Mode of version update\n\tmajor: Increment X in version X.Y.Z by 1"
                             "\n\tminor: Increment Y in version X.Y.Z by 1"
                             "\n\tpatch: Increment Z in version X.Y.Z by 1"
                             "\n\ttest: Use last git log commit hash as the tag and do not update the VERSION file")
    parser.add_argument("--version", dest='version', default="",
                        help="Specifically update docker image version of format X.Y.Z."
                             "\nWill not update image with latest tag.")
    parser.add_argument("--latest", dest='latest', action="store_true", default=False,
                        help="Update syangnub/nginx-uwsgi-falcon-server:latest")
    parser.add_argument("--yes", dest='yes', action="store_true", default=False, help="Do not ask for confirmation")
    parser.add_argument("--dry-run", dest='dry_run', action="store_true", default=False, help="Only build images and not push")
    parser.add_argument("--rmi", dest='rmi', help="Remove image specified as argument with rmi flag")

    args = parser.parse_args()

    if args.version:
        build_and_push_version(args.version, args.dry_run)
        if args.latest:
            build_and_push_latest(args.version, args.mode, args.dry_run, args.yes)

    if args.mode:
        version = build_and_push_mode(args.mode, args.dry_run)
        if args.latest:
            build_and_push_latest(version, args.mode, args.dry_run, args.yes)

    if args.rmi:
        clean_controller_images(args.rmi, 'a+')
