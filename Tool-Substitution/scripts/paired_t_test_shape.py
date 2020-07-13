from scipy import stats
import numpy as np
import pandas 

np.random.seed(11)

if __name__=="__main__":
	data_dual_nn = pandas.read_csv("/home/nithin/Desktop/Tool-Substitution-with-Shape-and-Material-ReasoningUsing-Dual-Neural-Networks/data/t_test/dual_nn_t_test_shape.csv")
	data_simple_nn = pandas.read_csv("/home/nithin/Desktop/Tool-Substitution-with-Shape-and-Material-ReasoningUsing-Dual-Neural-Networks/data/t_test/simple_nn_t_test_shape.csv")

	dnn_cut = np.array(data_dual_nn["CUT"])
	dnn_flip = np.array(data_dual_nn["FLIP"])
	dnn_hit = np.array(data_dual_nn["HIT"])
	dnn_poke = np.array(data_dual_nn["POKE"])
	dnn_rake = np.array(data_dual_nn["RAKE"])
	dnn_scoop = np.array(data_dual_nn["SCOOP"])
	dnn = np.concatenate((dnn_cut, dnn_flip, dnn_hit, dnn_poke, dnn_rake, dnn_scoop))
	print(dnn.shape)

	snn_cut = np.array(data_simple_nn["CUT"])
	snn_flip = np.array(data_simple_nn["FLIP"])
	snn_hit = np.array(data_simple_nn["HIT"])
	snn_poke = np.array(data_simple_nn["POKE"])
	snn_rake = np.array(data_simple_nn["RAKE"])
	snn_scoop = np.array(data_simple_nn["SCOOP"])
	snn = np.concatenate((snn_cut, snn_flip, snn_hit, snn_poke, snn_rake, snn_scoop))
	print(snn.shape)

	print(stats.ttest_rel(dnn, snn))