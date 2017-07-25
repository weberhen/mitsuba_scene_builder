import os
import argparse
import glob


def find_data_vpls(dir):
    # find all data_vpls.txt in the given root folder
    all_data_vpls = [os.path.join(dp, f) for dp, dn, filenames in os.walk(dir) for f in filenames
                     if f == 'data_vpls.txt']

    return all_data_vpls


def generate_meshes(all_data_vpls):
    # generate meshes to the data_vpls.txt that still do not have it
    for i in range(0, len(all_data_vpls)):
        if(not glob.glob((all_data_vpls[i][:-13] + 'mesh.ply'))):
            command = 'bash scripts/mesh_generator.sh ' + all_data_vpls[i][:-3] + 'ply' + ' ' + all_data_vpls[i][:-13] \
                      + 'mesh.ply'
            os.system(command)


def generate_config_files(all_data_vpls, args):
    # generate the configuration for the renders
        
    flag_skip_existing_render = ''
    if (args.skip_existing_render == True):
        flag_skip_existing_render = '-s '
    for i in range(0, len(all_data_vpls)):
    	#get name of the input folder to use it inside the dataset folder 
    	base_folder = "-".join(all_data_vpls[i].split('/')[-3:][:-1])
        command = 'python generateJSON.py ' + flag_skip_existing_render + '-v ' + all_data_vpls[i] + \
                  ' -o ' + args.output_location + '/' + base_folder
        os.system(command)


def generate_renders(all_data_vpls, args):
    # render all scenes

    for i in range(0, len(all_data_vpls)):
    	#get name of the input folder to use it inside the dataset folder 
    	base_folder = "-".join(all_data_vpls[i].split('/')[-3:][:-1])
        command = 'python main.py -b example/scene2.xml -c ' + args.output_location + '/' + base_folder + '/config.json ' + \
                  ' -o ' + args.output_location + '/' + base_folder
        os.system(command)


def main():
    # parse input
    parser = argparse.ArgumentParser(description='Render images for all ' + 'data_vpls.txt files found in the given ' \
                                                 + 'directory (recursively)')
    parser.add_argument('-i', '--input_location', help="folder with all data_vpls.txt's", required=True)
    parser.add_argument('-o', '--output_location', help="folder to store the dataset", required=True)
    parser.add_argument('-s', '--skip_existing_render', dest='skip_existing_render', action='store_true')
    args = parser.parse_args()

    all_data_vpls = find_data_vpls(args.input_location)

    generate_meshes(all_data_vpls)

    generate_config_files(all_data_vpls, args)

    generate_renders(all_data_vpls, args)


if __name__ == "__main__":
    main()
