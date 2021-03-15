clc
clear all

years=1898:2019;

%% Calculate R
for i=1:length(years)
    i
    if years(i)<2003 % FS3 series
        dummy=importdata(['time_series/KMI_FS3_' int2str(years(i)) '.txt']);
    else % 6447 series
        dummy=importdata(['time_series/KMI_6447_' int2str(years(i)) '.txt']);
    end
    table(i,:)=Calculate_R(years(i),dummy);
end

%% Output file
cHeader = {'jaar' 'erosiviteit' 'neerslagsom' '# regenbuien' '# erosieve regenbuien'}; %dummy header
commaHeader = [cHeader;repmat({','},1,numel(cHeader))]; %insert commas
commaHeader = commaHeader(:)';
textHeader = cell2mat(commaHeader); %cHeader in text with commas
%write header to file
fid = fopen('output.csv','w'); 
fprintf(fid,'%s\n',textHeader)
fclose(fid)
%write data to end of file
dlmwrite('output.csv',table,'-append');


