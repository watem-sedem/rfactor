%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%   R-factor 2 calculates the annual rainfall erosivity in metric    %%
%%  units (Mj*mm/(ha.h)), to be used in the RUSLE or USLE soil loss   %%
%% models, based on 10-minute rainfall data. The equations for the    %%
%% calculation of rainfall erosivity are taken from Renard et al. 1997%%
%% USDA agricultural Handbook 703, Washington, DC. This version also  %%
%% provides two-weekly and monthly erosivity values and annual erosi- %%
%% vity distributions and writes these to .txt files. It must be used %%
%%                with macro_Rfactor.m                                %%
%%                                                                    %%
%%                 written by Gert Verstraeten                        %%
%%           Laboratory for Experimental Geomorphology                %%
%%                 Department of Geography-Geology                    %%
%%                         KU Leuven                                  %%
%%           Redingenstraat 16, B-3000 Leuven, Belgium                %%
%%              gert.verstraeten@geo.kuleuven.ac.be                   %%
%%                                                                    %%
%%                          Rfactor 2.m                               %%
%%                           16-5-2001                                %%
%%								      %%
%%            edited by Johan Van de Wauw, Sacha Gobeyn	              %%
%%           			Fluves			              %%
%%           	Kerkstraat 106, Gentbrugge,Belgium                    %%
%%              	sacha@fluves.com			      %%
%%                                                                    %%
%%                            core.m                                  %%
%%                           16-03-2021                               %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function cumEI=core(year,rain)

r=1;

time=rain(:,1);
raindepth=rain(:,2); % omzetten naar mm
clear rain;
x=size(time);
x=x(1);
P(r)=sum(raindepth);

m=1;
timediff=0;
max=0;
c(1)=1;
for i=2:x
   timediff=(time(i)-time(i -1));
   if timediff>=360 %tijd tussen twee buien groter dan 6 uur=nieuwe bui
      m=m+1;
      c(m)=i; %begin van de nieuwe bui
      d=c(m)-c(m-1);
      if d>max
         max=d;
      end
   end
end


% isoleren van individuele regenbuien
pluviophase(:,max,m)=0;
for i=1:(m-1)
   begin=c(i);
   eind=c(i+1)-1;
   a=begin;
   b=eind-begin+1;
   pluviophase(1,1:b,i)=time(begin:eind);
   pluviophase(2,1:b,i)=raindepth(begin:eind);
end
begin=eind+1;
eind=x;
b=eind-begin+1;
pluviophase(1,1:b,m)=time(begin:eind);
pluviophase(2,1:b,m)=raindepth(begin:eind);
for i=1:m
   k=10;
   maxtime(i)=pluviophase(1,1,i);
   for j=1:max
      if pluviophase(1,j,i)>maxtime(i)
         maxtime(i)=pluviophase(1,j,i);
      end
   end
   for j=1:max
      if pluviophase(1,j,i)==0
         pluviophase(1,j,i)=maxtime(i)+k;
         k=k+10; % is nodig voor interpolatie achteraf: x must be monotonic !!
      end
   end
end

clear raindepth;
clear time;

% berekenen van cumulatieve neerslag per bui
for i=1:m
   pluviophase(3,1,i)=pluviophase(2,1,i);
   for j=2:max
      pluviophase(3,j,i)=pluviophase(3,j-1,i)+pluviophase(2,j,i);
   end
end



E(1:m)=0;
t=0;
for i=1:m
   pluviophase(4,1,i)=pluviophase(2,1,i)*6;
   pluviophase(5,1,i)=0.1112*(pluviophase(4,1,i)^0.31);  % berekenen van neerslagenergie per mm
   % totale neerslagenergie
   E(i)=E(i)+pluviophase(5,1,i)*pluviophase(2,1,i);
   cumul(i)=t;
   t=t+pluviophase(3,max,i);
   for j=2:max
      pluviophase(4,j,i)=pluviophase(2,j,i)*6;
      pluviophase(5,j,i)=0.1112*(pluviophase(4,j,i)^0.31); % berekenen van neerslagenergie per mm
      % totale neerslagenergie
      E(i)=E(i)+pluviophase(5,j,i)*pluviophase(2,j,i);
   end
end


%berekenen van maximale neerslagintensiteit in 30 minuten
for i=1:m

   maxP30=0;

   maxprecip30min(i)=0;
   a=pluviophase(1,:,i);
   b=pluviophase(3,:,i);

   for j=1:max-2
      begin30min=pluviophase(1,j,i);
      eind30min=begin30min+20;
      beginprecip=pluviophase(3,j,i)-pluviophase(2,j,i);
      if pluviophase(1,j+1,i)>eind30min
         maxprecip30min(i)=pluviophase(2,j,i);
      elseif pluviophase(1,j+1,i)==(begin30min+20)
         eindprecip=pluviophase(3,j+1,i);
         precip30min=eindprecip-beginprecip;
      elseif pluviophase(1,j+1,i)==(begin30min+10)
         if pluviophase(1,j+2,i)==(begin30min+20)
            eindprecip=pluviophase(3,j+2,i);
         else
            eindprecip=pluviophase(3,j+1,i);
         end
         precip30min=eindprecip-beginprecip;
      else
         % test
      end

      % veronderstel uniforme vulling van bakje
      eindprecip=interp1(a,b,eind30min);
      precip30min=eindprecip-beginprecip;
      if precip30min>maxprecip30min(i)
         maxprecip30min(i)=precip30min;
      end

      if maxprecip30min(i)>maxP30
         maxP30=maxprecip30min(i);
      end
      if (maxtime(i)-pluviophase(1,1,i))<=30
         maxP30=pluviophase(3,max,i);
      end

      I30(i)=(maxP30*2); % maximale I in 30 opeenvolgende minuten (mm/h)

   end
end


a=sum(pluviophase(2,:,:));   %berekenen van de totale neerslagsom voor elke regenbui (mm)


for i=1:m
   if a(i)<1.27
      EI(1:3,i)=0;
   else
      EI(2,i)=E(i)*I30(i); % erosiviteit per bui
      EI(1,i)=pluviophase(1,1,i)/1440; % begintijdstip van de bui in dagen
      EI(3,i)=cumul(i); %cumulatieve neerslag
   end
end

clear pluviophase;
clear a;
clear b;
clear c;

% berekenen van cumulatieve erosiviteit

cumEI(1,1)=EI(1,1);
cumEI(2,1)=EI(2,1);
cumEI(3,1)=EI(3,1);
cumEI(4,1)=EI(2,1);
k=2;
for i=2:m
   if EI(1,i)>0
      cumEI(1,k)=EI(1,i);
      cumEI(2,k)=EI(2,i)+cumEI(2,k-1);
      cumEI(3,k)=EI(3,i);
      cumEI(4,k)=EI(2,i)
      erobui(1,k-1)=EI(2,i);
      erobui(2,k-1)=EI(1,i);
      k=k+1;
   else
      k=k;
   end
end

% berekenen van maandelijkse erosiviteit
Rm(r,1:12) = 0;

for i=1:k-1
   if cumEI(1,i)<=31
      Rm(r,1)=cumEI(2,i);
   elseif cumEI(1,i)<=59
      cumM(1:11)=cumEI(2,i);
      Rm(r,2)=cumM(1)-Rm(r,1);
   elseif cumEI(1,i)<=90
      cumM(2:11)=cumEI(2,i);
      Rm(r,3)=cumEI(2,i)-cumM(1);
   elseif cumEI(1,i)<=120
      cumM(3:11)=cumEI(2,i);
      Rm(r,4)=cumEI(2,i)-cumM(2);
   elseif cumEI(1,i)<=151
      cumM(4:11)=cumEI(2,i);
      Rm(r,5)=cumEI(2,i)-cumM(3);
   elseif cumEI(1,i)<=181
      cumM(5:11)=cumEI(2,i);
      Rm(r,6)=cumEI(2,i)-cumM(4);
   elseif cumEI(1,i)<=212
      cumM(6:11)=cumEI(2,i);
      Rm(r,7)=cumEI(2,i)-cumM(5);
   elseif cumEI(1,i)<=243
      cumM(7:11)=cumEI(2,i);
      Rm(r,8)=cumEI(2,i)-cumM(6);
   elseif cumEI(1,i)<=273
      cumM(8:11)=cumEI(2,i);
      Rm(r,9)=cumEI(2,i)-cumM(7);
   elseif cumEI(1,i)<=304
      cumM(9:11)=cumEI(2,i);
      Rm(r,10)=cumEI(2,i)-cumM(8);
   elseif cumEI(1,i)<=334
      cumM(10:11)=cumEI(2,i);
      Rm(r,11)=cumEI(2,i)-cumM(9);
   elseif cumEI(1,i)<=366
      cumM(11)=cumEI(2,i);
      Rm(r,12)=cumEI(2,i)-cumM(10);
   end
end

% berekenen van tweewekelijkse erosiviteit
dag=14;
c=cumEI(1,1:k-1);
d=cumEI(2,1:k-1);
e=cumEI(3,1:k-1);
cumD14(1)=interp1(c,d,dag);
cumP14(1)=interp1(c,e,dag);
D14(r,1)=cumD14(1);
P14(r,1)=cumP14(1);
for p=2:25
   dag=dag+14;
   if (p==25) && (cumEI(1,k-1)<351)
      cumD14(p)=sum(EI(2,:));
      cumP14(p)=P(r);
      D14(r,25)=cumD14(25)-cumD14(24);
      P14(r,25)=cumP14(25)-cumP14(24);
   else
      cumD14(p)=interp1(c,d,dag);
      cumP14(p)=interp1(c,e,dag);
      D14(r,p)=cumD14(p)-cumD14(p-1);
      P14(r,p)=cumP14(p)-cumP14(p-1);
   end
end
cumD14(26)=sum(EI(2,:));
cumP14(26)=P(r);
D14(r,26)=cumD14(26)-cumD14(25);
P14(r,26)=cumP14(26)-cumP14(25);

end
