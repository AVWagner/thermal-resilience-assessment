# thermal-resilience-assessment
Scripts used for my Building-Technology Master Thesis: "Decision-making for enhanced thermal resilience of façade-retrofits"
The research aims to improve the design process of retrofit options, increasing thermal indoor comfort during heat waves. 
Resilience indices are developed, that assess the facade's performance in identified stages of a resilient response to extreme heat. 
Based on the current state of the facade, local building standards or requirements, and realistic retrofit options, possible facacde variables can be identified as retrofit variables. 
Their possible impact is calculated using the SOBOL sensitivity analysis. Postprocessing the results, different variables per resilience stage can be identified, which can be used as an indication during the design process of the facade-retrofit. 

Workflow: 
The proposed simulation workflow requires an IDF of the current state scenario (including all relevant building parameters). 
1. "Sensitivity analysis" 

2. Postprocessing 
2.1 "SA_performance_analysis"
2.2 "SA_performance_analysis_best overall"
2.3 "SA_variable_values_analysis"

3. Evaluation
3.1 "Retrofit_index calculation"

Note that following libraries are used: 
EPPY: Santosh, P. (2022). Eppy Documentation. https://buildmedia.readthedocs.org/media/pdf/eppy/latest/eppy.pdf
NUMPY Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., Cournapeau, D., Wieser, E., Taylor, J., Berg, S., Smith, N. J., Kern, R., Picus, M., Hoyer, S., van Kerkwijk, M. H., Brett, M., Haldane, A., del Río, J. F., Wiebe, M., Peterson, P., … Oliphant, T. E. (2020). Array programming with NumPy. Nature, 585(7825), 357–362. https://doi.org/10.1038/s41586-020-2649-2
PYTHERMALCOMFORT Tartarini, F., & Schiavon, S. (2020). pythermalcomfort: A Python package for thermal comfort research. SoftwareX, 12, 100578. https://doi.org/10.1016/j.softx.2020.100578
SALib Herman, J., & Usher, W. (2017). SALib: An open-source Python library for Sensitivity Analysis. The Journal of Open Source Software, 2(9), 97. https://doi.org/10.21105/joss.00097
