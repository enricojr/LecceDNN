#####
##### script to launch 12 jobs for mc12a/d/e -> merged/resolved -> ggF/VBF for a given signal given defined as input 
##### 
signal=$1 
mynode=`cat /proc/sys/kernel/hostname`
mynodes=${mynode:0:5}
tag=`date +"%Y%m%d_%H_%M_%S"`
###
### mc16a 
log=log_addScores_all_resolved_ggF_${signal}_mc16a_${tag}
nohup ./addScores.sh all resolved ggF ${signal} mc16a > /scratch/stefania/${log} &
ln -sf /scratch/stefania/${log} ./logs/${log}_${mynodes}; sleep 3s

log=log_addScores_all_resolved_VBF_${signal}_mc16a_${tag}
nohup ./addScores.sh all resolved VBF ${signal} mc16a > /scratch/stefania/${log} &
ln -sf /scratch/stefania/${log} ./logs/${log}_${mynodes}; sleep 3s

log=log_addScores_all_merged_ggF_${signal}_mc16a_${tag}
nohup ./addScores.sh all merged ggF ${signal} mc16a > /scratch/stefania/${log} &
ln -sf /scratch/stefania/${log} ./logs/${log}_${mynodes}; sleep 3s

log=log_addScores_all_merged_VBF_${signal}_mc16a_${tag}
nohup ./addScores.sh all merged VBF ${signal} mc16a > /scratch/stefania/${log} &
ln -sf /scratch/stefania/${log} ./logs/${log}_${mynodes}; sleep 3s

### mc16d 
log=log_addScores_all_resolved_ggF_${signal}_mc16d_${tag}
nohup ./addScores.sh all resolved ggF ${signal} mc16d > /scratch/stefania/${log} &
ln -sf /scratch/stefania/${log} ./logs/${log}_${mynodes}; sleep 3s

log=log_addScores_all_resolved_VBF_${signal}_mc16d_${tag}
nohup ./addScores.sh all resolved VBF ${signal} mc16d > /scratch/stefania/${log} &
ln -sf /scratch/stefania/${log} ./logs/${log}_${mynodes}; sleep 3s

log=log_addScores_all_merged_ggF_${signal}_mc16d_${tag}
nohup ./addScores.sh all merged ggF ${signal} mc16d > /scratch/stefania/${log} &
ln -sf /scratch/stefania/${log} ./logs/${log}_${mynodes}; sleep 3s

log=log_addScores_all_merged_VBF_${signal}_mc16d_${tag}
nohup ./addScores.sh all merged VBF ${signal} mc16d > /scratch/stefania/${log} &
ln -sf /scratch/stefania/${log} ./logs/${log}_${mynodes}; sleep 3s

## mc16e 
log=log_addScores_all_resolved_ggF_${signal}_mc16e_${tag}
nohup ./addScores.sh all resolved ggF ${signal} mc16e > /scratch/stefania/${log} &
ln -sf /scratch/stefania/${log} ./logs/${log}_${mynodes}; sleep 3s

log=log_addScores_all_resolved_VBF_${signal}_mc16e_${tag}
nohup ./addScores.sh all resolved VBF ${signal} mc16e > /scratch/stefania/${log} &
ln -sf /scratch/stefania/${log} ./logs/${log}_${mynodes}; sleep 3s

log=log_addScores_all_merged_ggF_${signal}_mc16e_${tag}
nohup ./addScores.sh all merged ggF ${signal} mc16e > /scratch/stefania/${log} &
ln -sf /scratch/stefania/${log} ./logs/${log}_${mynodes}; sleep 3s

log=log_addScores_all_merged_VBF_${signal}_mc16e_${tag}
nohup ./addScores.sh all merged VBF ${signal} mc16e > /scratch/stefania/${log} &
ln -sf /scratch/stefania/${log} ./logs/${log}_${mynodes}; sleep 3s

