#!/usr/bin/env python

import qarnot
import os
import os.path
import sys
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-b", "--background",   type=str,   required=True)
    parser.add_argument("-s", "--frame-start",  type=str,   required=False)
    parser.add_argument("-e", "--frame-end",    type=str,   required=False)
    parser.add_argument("-f", "--render-frame", type=str,   required=False)
    parser.add_argument("-E", "--engine",       type=str,   required=False,
                        choices=['', 'BLENDER_RENDER', 'BLENDER_GAME',
                                 'CYCLES'])
    parser.add_argument("-F", "--render-format",type=str,   required=False,
                        choices=['', 'MULTILAYER', 'EXR', 'JPEG', 'TGA',
                                 'PNG'])
    parser.add_argument("-S", "--scene",        type=str,   required=False)
    parser.add_argument("-o", "--render-output",type=str,   required=False)
    parser.add_argument("--factory-startup", action="store_true")

    args, _ = parser.parse_known_args()
    input_file = args.background
    task_name = 'blender-'+os.path.basename(input_file)

    # Create a connection, from which all other objects will be derived
    conn = qarnot.Connection('qarnot.conf')

    # Create a task.
    task = conn.create_task(task_name, 'blender-2.79', 0)

    # Store if an error happened during the process
    error_happened = False
    try:
        # Create a resource bucket and synchronize files
        input_bucket = conn.retrieve_or_create_bucket(task_name + '-resource')
        if os.sep in input_file:
            file_path = os.path.dirname(input_file) + os.sep
            input_bucket.sync_directory(file_path, True, remote=file_path)
        else:
            input_bucket.sync_files({input_file:input_file}, True)

        # Attach the bucket to the task
        task.resources.append(input_bucket)

        # create and attach output bucket
        output_bucket = conn.retrieve_or_create_bucket(task_name + '-results')
        task.results = output_bucket

        # Define render range
        if args.render_frame is not None:
            task.advanced_range = args.render_frame
        else:
            if args.frame_start is not None and args.frame_end is not None:
                task.advanced_range = args.frame_start + '-' + args.frame_end
            elif args.frame_start is not None:
                task.advanced_range = args.frame_start
            else:
                sys.stderr.write("Please chose a frame or a range to render.\n")
                sys.exit(2)

        engine = args.engine if args.engine is not None else "CYCLES"
        out_format = args.render_format if args.render_format is not None else 'PNG'

        # Task constants are the main way of controlling a task's behaviour
        task.constants['BLEND_FILE'] = input_file
        task.constants['BLEND_ENGINE'] = engine
        task.constants['BLEND_FORMAT'] = out_format
        if args.scene is not None:
            task.constants['BLEND_SCENE'] = args.scene
        if args.render_output is not None:
            task.constants['BLEND_OUTPUT'] = args.render_output
        # Submit the task to the Api, that will launch it on the cluster
        task.submit()

        # Wait for the task to be finished, and monitor its progress
        last_state = ''
        last_execution_progress = 0.0
        done = False
        while not done:
            if task.status is not None and task.status.execution_progress != last_execution_progress:
                last_execution_progress = task.status.execution_progress
                print("** Overall progress {}%".format(last_execution_progress))

            if task.state != last_state:
                last_state = task.state
                print("** {}".format(last_state))

            # Wait for the task to complete, with a timeout of 5 seconds.
            # This will return True as soon as the task is complete, or False
            # after the timeout.
            done = task.wait(5)

            # Display fresh stdout / stderr
            sys.stdout.write(task.fresh_stdout())
            sys.stderr.write(task.fresh_stderr())

        # Display errors on failure
        if task.state == 'Failure':
            print("** Errors: %s" % task.errors[0])
            error_happened = True

        # Download succeeded frames
        task.download_results('output')
    finally:
        # Exit code in case of error
        if error_happened:
            sys.exit(1)
