#%%function to bin m/z in a given tolerance
def group_mz(mz, intensities, tolerance=0.005):
    import numpy as np
    
    sort = np.argsort(mz)
    sorted_mz = mz[sort]
    sorted_ints = intensities[sort]
   
    groups_mz = [] 
    groups_int = []
    
    current_group_mz = [sorted_mz[0]]
    current_group_int = [sorted_ints[0]]
    
    for i in range(1,len(sorted_mz)):
        if np.abs(sorted_mz[i] - current_group_mz[-1]) < tolerance:
            current_group_mz.append(sorted_mz[i])
            current_group_int.append(sorted_ints[i])   
        else:
            groups_mz.append(current_group_mz)
            current_group_mz = [sorted_mz[i]]
            
            groups_int.append(current_group_int)
            current_group_int = [sorted_ints[i]]
            
    groups_mz.append(current_group_mz)
    groups_int.append(current_group_int)
    
    return groups_mz, groups_int

#%%helper functions to determine average, median and sum of list of lists
def average_lists(lists):
    averages = []
    for lst in lists:
        avg = sum(lst) / len(lst)
        averages.append(avg)
    return averages

def sum_lists(lists):
    sums = []
    for lst in lists:
        s = sum(lst)
        sums.append(s)
    return sums

def median_lists(lists):
    medians = []
    for lst in lists:
        lst.sort()
        n = len(lst)
        if n % 2 == 0:
            median = (lst[n//2] + lst[n//2-1]) / 2
        else:
            median = lst[n//2]
        medians.append(median)
    return medians

#%%
def consensus_spectrum(x, mzd = 0.005, minProp = 0.6, 
                       intensityFun = "sum", mzFun = "median"):
    
    import numpy as np
    from matchms import Spectrum
    from itertools import compress
    
    # if only one spectrum present return 
    if len(x) == 1:
        print("Only single spectrum supplied.")
        return x[0]
    
    # Convert x to list of matchms.Spectrum objects if needed
    if not isinstance(x, list):
        x = [x]
    
    # Check that all spectra have the same MS level
    if len(set(spectrum.get("ms_level") for spectrum in x)) != 1:
        raise ValueError("Can only combine spectra with the same MS level.")
    
    # Get m/z and intensity values for all spectra
    mz_values = []
    intensity_values = []

    for spectrum in x:
        mz_values.append(spectrum.peaks.mz)
        intensity_values.append(spectrum.peaks.intensities)
        
    mz_values = np.concatenate(mz_values)
    intensity_values = np.concatenate(intensity_values)
    
    # Remove peaks with zero intensity
    keep = intensity_values > 0
    mz_values = mz_values[keep]
    intensity_values = intensity_values[keep]
    
    # Group peaks by m/z values with given tolerance (mzd or ppm)
    mz_groups, int_groups = group_mz(mz_values, intensity_values, tolerance = mzd)

    # Keep only groups that appear in more than minProp% of spectra
    group_lengths = [len(group) for group in mz_groups]
    keep = np.array(group_lengths) >= len(x) * minProp    
      
    mz_groups = list(compress(mz_groups, keep))
    int_groups = list(compress(int_groups, keep))
    
    # if peaks met the consensus criteria:
    if len(mz_groups) > 0:
        
        # different options for intensity calculation
        if intensityFun == "mean":
            intensity = average_lists(int_groups)
        if intensityFun == "sum":
            intensity = sum_lists(int_groups)
         
        # different options for m/z calculation
        if mzFun == "median":   
            mz = median_lists(mz_groups)
        if mzFun == "mean":
            mz = average_lists(mz_groups)
            
    else:
        print(f"No peak present in more than {minProp*100}% of spectra.")

    
    # extract metadata for new consensus spectrum
    prec_mz = []
    prec_int = []
    rt = []
    
    for s in range(len(x)):
        prec_mz.append(x[s].get("precursor_mz")) 
        prec_int.append(x[s].get("precursor_intensity")) 
        rt.append(x[s].get("retention_time")) 
        
    prec_mz = np.average(np.array(prec_mz))
    prec_int = np.average(np.array(prec_int))
    rt = np.average(np.array(rt))
    
    # create the spectrum
    cs = Spectrum(mz = np.array(mz),
                  intensities = np.array(intensity),
                  metadata={'peaksCount': len(mz),
                            'precursor_mz': prec_mz,
                            'precursor_intensity': prec_int,
                            'retention_time': rt})
   
    return cs

#%%currently unused

class ConsensusSpectrum():
    # comment
    
    def __init__(self, mz = []):
        self.mz = mz
        self.int = []
        self.rt = []
        self.polarity = []
        self.mslevel = int()
        self.precmass = float()
        self.metadata = []
        
        
    def fun1(self):
        self.y += 1