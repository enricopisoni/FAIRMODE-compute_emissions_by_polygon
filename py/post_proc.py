import os
from glob import glob

import fairmode_parameters


def merge_all(output_path, checked_files_no, admin_filter, merge_target):
    """Put together csv files in a single one

    :param output_path:  input folder (with list of previously created csv)
    :param checked_files_no: check how many files...
    :param admin_filter: which admin we are testing (last part of each single file_name)
    :param merge_target: final full output file_name
    """

    search_filter=os.path.join(output_path, '*_'+admin_filter+'*.csv')
    file_list = glob(search_filter)

    output_file = merge_target
    if checked_files_no != len(file_list) or len(file_list) == 0:
        print('wrong files in folder, for ', admin_filter, 'expected:',checked_files_no, 'found:',len(file_list))
        return

    try:
        os.remove(merge_target)
    except FileNotFoundError:
        pass
    with open(merge_target, "ab") as fout:
        # First file (with header):
        #print('write first')
        with open(file_list[0], "rb") as f:
            fout.writelines(f)

        # Now the rest:
        #print('write the rest')
        for num in range(1, len(file_list)):
            with open(file_list[num], "rb") as f:
                next(f)  # Skip the header, portably
                fout.writelines(f)


def check_missing_poll_sect_combination(output_path, selected_admin):
    """Check all the combination of pollutants/sectors (for a specific admin code)

    :param output_path:  input folder (with list of previously created csv)
    :param selected_admin: which admin we are testing (last part of each single file_name)
    :return boolean: number of expected files is good
            int: number of correct files
            string: suggested output file_name
    """

    search_filter=os.path.join(output_path, '*'+selected_admin+'*.csv')
    file_list = glob(search_filter)

    polls=fairmode_parameters.get_valid_poll()
    sector_codes, sector_desc, sector_mixed_codes=fairmode_parameters.get_valid_sectors()
    missing = False
    found = False
    i=0
    model = 'N/A'
    year = 'N/A'
    # use main_admin when we have FUA-UK and FUA-EU --> merge will be put together in FUA.csv (issue: do it twice)

    for poll in polls:
        for sect in sector_codes:
            print('looking for poll:', poll,'sect: ', sect,'poly: ', selected_admin)

            for test_file in file_list:
                #print(test_file)
                model, institution, file_sect, file_poll, file_admin = os.path.basename(
                    test_file).split("_")
                file_admin, ext = file_admin.split(".")
                #main_admin = main_admin.split("-")
                print(model, institution, file_sect, file_poll, file_admin)

                if poll == file_poll and sect == file_sect and file_admin == selected_admin:
                    print('Found combination pollutant: ', poll, ' + sect ', sect, 'poly: ', selected_admin, '--->', test_file)
                    i=i+1
                    found = True
                    break
            if not(found):
                #print('Warning: Missing *csv* file for pollutant: ', poll, ' and sect: ', sect,
                #    ' and poly: ', selected_admin)
                missing = True
            found=False
    return not(missing), i, model+'_'+institution+'_'+file_admin


def finalize(split_folder, merge_target_folder):
    """Do all the checks for each predefined admin/polygons

    :param split_folder:  input folder (with list of previously created csv)
    :param merge_target_folder: final merged csv folder
    """

    admin_class = fairmode_parameters.get_admin_id_class()

    for i, admin in enumerate(admin_class):

        print('admin', admin)
        main_admin = admin.split("-")[0]

        check, file_count, name = check_missing_poll_sect_combination(split_folder, main_admin)
        print('check, file_count, name', check, file_count, name)
        final_name = os.path.join(merge_target_folder, name + '.csv')
        check = True
        if check:
            print(split_folder, file_count, main_admin, 'merge to -->', final_name)
            merge_all(split_folder, file_count, main_admin, final_name)

