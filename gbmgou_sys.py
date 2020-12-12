import numpy as np

class GBM_SDE():
    
    def __init__(self,dt):
        self.mu = []
        self.sigma = []
        self.dt = dt
        
    def add_mu_MLE(self,data):
        global barmu_MLE
        self.mu.append(barmu_MLE(data))
        
    def add_sigma_MLE(self,data):
        global sigma_MLE
        self.sigma.append(sigma_MLE(data,self.mu[-1],self.dt))

class GOU_SDE():
    
    def __init__(self,dt):
        self.ekappa = []
        self.bartheta = []
        self.sigma = []
        self.dt = dt
        
    def add_ekappa_MLE(self,data):
        global ekappa_MLE
        self.ekappa.append(ekappa_MLE(data))
        
    def add_bartheta_MLE(self,data):
        global bartheta_MLE
        self.bartheta.append(bartheta_MLE(data,self.ekappa[-1]))
        
    def add_sigma_MLE(self,data):
        global sigma2_MLE
        self.sigma.append(sigma2_MLE(data,
                          self.ekappa[-1],
                          self.bartheta[-1],
                          self.dt))

class GBM_GOU_System():
    
    def __init__(self,num_GBM,num_GOU,dt):
        
        self.sde_list = []
        
        for i in range(num_GBM):
            self.sde_list.append(GBM_SDE(dt),True)
            
        for i in range(num_GBM,num_GBM+num_GOU):
            self.sde_list.append(GOU_SDE(dt),False)
            
        self.corr_mat = []
        self.dt = dt
        
    def is_GBM(self,idx):
        return self.sde_list[idx][1]
    
    def update_system(self,indata):
        
        corrmat = np.zeros((len(self.sde_list),len(self.sde_list)))
        
        for idx,SDE in enumerate(self.sde_list):
            
            data = indata[idx]
            
            if SDE[1]:
                SDE[0].add_mu_MLE(data)
                SDE[0].add_sigma_MLE(data)
            else:
                SDE[0].add_ekappa_MLE(data)
                SDE[0].add_bartheta_MLE(data)
                SDE[0].add_sigma_MLE(data)
        
        for i in range(len(self.sde_list)):
                           
            for j in range(i+1,len(self.sde_list)):
                
                if self.is_GBM(i) == True and self.is_GBM(j) == True:
                    
                    sde_i = self.sde_list[i]
                    sde_j = self.sde_list[j]
                    
                    par1 = np.log(indata[i][1:])-np.log(data[i][:-1])-sde_i.mu[-1]*self.dt
                    par2 = np.log(indata[j][1:])-np.log(data[j][:-1])-sde_j.mu[-1]*self.dt
                    
                    corrmat[i][j] = np.mean(par1*par2)/(sde_i.sigma[-1]*sde_j.sigma[-1]*self.dt)
                    
                elif self.is_GBM(i) == False and self.is_GBM(j) == False:
                    
                    sde_i = self.sde_list[i]
                    sde_j = self.sde_list[j]
                    
                    par1 = np.log(indata[i][1:])-sde_i.bartheta[-1]*\
                    (np.log(indata[i])[:-1]-sde_i.bartheta[-1])*sde_i.ekappa*self.dt
                    par2 = np.log(indata[j][1:])-sde_j.bartheta[-1]*\
                    (np.log(indata[j])[:-1]-sde_j.bartheta[-1])*sde_j.ekappa*self.dt
                    
                    corrmat[i][j] = (np.log(sde_i.ekappa[-1]*sde_j.ekappa[-1]))*np.mean(par1*par2)/\
                    (sde_i.sigma[-1]*sde_j.sigma[-1]*(1-sde_i.ekappa[-1]*sde_j.ekappa[-1]))
                    
                elif self.is_GBM(i) == False and self.is_GBM(j) == True:
                    
                    sde_i = self.sde_list[i]
                    sde_j = self.sde_list[j]
                    
                    par1 = np.log(indata[i][1:])-sde_i.bartheta[-1]*\
                    (np.log(indata[i])[:-1]-sde_i.bartheta[-1])*sde_i.ekappa*self.dt
                    par2 = np.log(indata[j][1:])-np.log(data[j][:-1])-sde_j.mu[-1]*self.dt
                    
                    corrmat[i][j] = np.log(sde_i.ekappa[-1])/(sde_i.sigma[-1]*sde_j.sigma[-1]*(1-sde_i.ekappa[-1]))*\
                    np.mean(par1*par2)
                    
                else:
                    
                    
                    sde_i = self.sde_list[i]
                    sde_j = self.sde_list[j]
                    
                    par1 = np.log(indata[j][1:])-sde_j.bartheta[-1]*\
                    (np.log(indata[j])[:-1]-sde_j.bartheta[-1])*sde_j.ekappa*self.dt
                    par2 = np.log(indata[i][1:])-np.log(data[i][:-1])-sde_i.mu[-1]*self.dt
                    
                    corrmat[i][j] = np.log(sde_j.ekappa[-1])/(sde_j.sigma[-1]*sde_i.sigma[-1]*(1-sde_j.ekappa[-1]))*\
                    np.mean(par1*par2)
                    
        self.corr_mat.append(corrmat)
        
    def predict(self,i):
        return None
