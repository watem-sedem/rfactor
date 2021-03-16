
function []=script(path)

    %% Prepare
    mkdir("results")

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
       [pathstr,name,ext]=fileparts(filename);
       year = split(name,"_");
       year = year(length(year));
       year = str2double(year{1});
       % Import inputdata
       inputdata=importdata(filename);
       % Calculate R
       [R, cumEI]=Calculate_R(year,inputdata);
       table(i,:)=R;
       % Prepare write
       fid = fopen(fullfile('results',[name,'new cumdistr salles.txt']),'wt');
       % write the matrix
       if fid > 0
           fprintf(fid,'%.3f %.2f %.1f\n',cumEI);
           fclose(fid);
       end
    end

    %% Calculate R
    %for i=1:length(years)
    %    i
    %    if years(i)<2003 % FS3 series
    %        dummy=importdata(['time_series/KMI_FS3_' int2str(years(i)) '.txt']);
    %    else % 6447 series
    %        dummy=importdata(['time_series/KMI_6447_' int2str(years(i)) '.txt']);
    %    end
    %    table(i,:)=Calculate_R(years(i),dummy);
    %
    %% Output file
    cHeader = {'jaar' 'erosiviteit' 'neerslagsom' '# regenbuien' '# erosieve regenbuien'}; %dummy header
    commaHeader = [cHeader;repmat({','},1,numel(cHeader))]; %insert commas
    commaHeader = commaHeader(:)';
    textHeader = cell2mat(commaHeader); %cHeader in text with commas
    %write header to file
    fid = fopen(fullfile('results','output.csv'),'w'); 
    fprintf(fid,'%s\n',textHeader)
    fclose(fid)
    %write data to end of file
    table;
    dlmwrite('output.csv',table,'-append');




