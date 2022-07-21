- The dataset.csv contains 50 datasets for no. of locations = 2 to 6, 10 datasets for each no. of location.

- For a dataset of a particular no. of locations, we have generated x and y coordinates of each location and a weight matrix depicting the weight of an edge between two locations.

- The x and y coordinates and weight matrix of a particular dataset of a particular no. of locations have been made as an numpy array and converted to pandas dataframe and saved as a csv file, they are named as x_i_j, y_i_j, and wm_i_j respectively. Here, i represents the no. of locations and j (j goes from 0 to 9, representing 10 different datasets) represents the particular dataset number of a "i" no. of locations instance. Here, wm_i_j is a nxn matrix which represents the edge weight for each 2 nodes selected.

- For example, x_4_6, y_4_6, wm_4_6 are the only data required for running an experiment corresponding to an instance with no. of locations = 4. Here, 6 represents that this is the 7th dataset for no. of locations = 4.

- This dataset.csv can be converted into the required format such as numpy array, pandas dataframe using various functions from csv, pandas, numpy libraries.

- A dataset generating notebook has also been provided in this directory for generating your own instances with the range of no. of locations you might need. You may also set how many datasets you want to generate for a particular no. of locations. Instructions for all this has been provided in that notebook.
 
