
function []=main(path,path_results)

    %% Check if directory exists
    if ~exist(path, 'dir')
        error('Cannot find inputfolder')
    end
    %% Loop files and calculate R
    files = dir(fullfile(path,'*.txt')); %%get all text files of the present folder
    files;
    N = length(files) ;  % Total number of files
    for i = 1:N
       % Prepare filename
       filename = fullfile(path,files(i).name);
       disp(filename)
       [pathstr,name,ext]=fileparts(filename);
       year = strsplit(name,"_");
       year = year(length(year));
       year = str2double(year{1});
       % Import inputdata
       inputdata=importdata(filename);
       % Calculate R
       cumEI=core(year,inputdata);
       % Prepare write
       filename_out=fullfile(path_results,strcat(name,'new cumdistr salles.txt'));
       fid = fopen(filename_out,'wt');
       disp(filename_out)
       % write the matrix
       if fid > 0
           fprintf(fid,'%.3f %.2f %.1f %.2f\n',cumEI);
           fclose(fid);
       end
    end
