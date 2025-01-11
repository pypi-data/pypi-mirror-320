

#include "set_parameters.h"

using namespace std;

namespace oslom{

void general_program_statement(char * b) {
	
	
	spdout<<"USAGE: "<<b<<" -f network.dat -uw(-w)"<<"\n"<<"\n";
	spdout<<"-uw must be used if you want to use the unweighted null model; -w otherwise."<<"\n";
	spdout<<"network.dat is the list of edges. Please look at ReadMe.pdf for more details."<<"\n";
	
	
	
	spdout<<"\n\n\n";
	spdout<<"***************************************************************************************************************************************************"<<"\n";
	spdout<<"OPTIONS"<<"\n";	
	spdout<<"\n  [-r R]:\t\t\tsets the number of runs for the first hierarchical level, bigger this value, more accurate the output (of course, it takes more). Default value is 10."<<"\n";
	spdout<<"\n  [-hr R]:\t\t\tsets the number of runs  for higher hierarchical levels. Default value is 50 (the method should be faster since the aggregated network is usually much smaller)."<<"\n";
	spdout<<"\n  [-seed m]:\t\t\tsets m equal to the seed for the random number generator. (instead of reading from time_seed.dat)"<<"\n"; 
	spdout<<"\n  [-hint filename]:\t\ttakes a partition from filename. The file is expected to have the nodes belonging to the same cluster on the same line."<<"\n";
	spdout<<"\n  [-load filename]:\t\ttakes modules from a tp file you already got in a previous run."<<"\n";
	spdout<<"\n  [-t T]:\t\t\tsets the threshold equal to T, default value is 0.1"<<"\n";
	spdout<<"\n  [-singlet]:\t\t\t finds singletons. If you use this flag, the program generally finds a number of nodes which are not assigned to any module.\n\t\t\t\t";
	spdout<<"the program will assign each node with at least one not homeless neighbor. This only applies to the lowest hierarchical level."<<"\n";
	spdout<<"\n  [-cp P]:\t\t\tsets a kind of resolution parameter equal to P. This parameter is used to decide if it is better to take some modules or their union.\n\t\t\t\tDefault value is 0.5. ";
	spdout<<"Bigger value leads to bigger clusters. P must be in the interval (0, 1)."<<"\n";
	spdout<<"\n  [-fast]:\t\t\tis equivalent to \"-r 1 -hr 1\" (the fastest possible execution)."<<"\n";
	spdout<<"\n  [-infomap runs]:\t\tcalls infomap and uses its output as a starting point. runs is the number of times you want to call infomap."<<"\n";
	spdout<<"\n  [-copra runs]:\t\tsame as above using copra."<<"\n";
	spdout<<"\n  [-louvain runs]:\t\tsame as above using louvain method."<<"\n";
	spdout<<"\n\nPlease look at ReadMe.pdf for a more detailed explanation."<<"\n";



	spdout<<"\n\n\n";
	spdout<<"***************************************************************************************************************************************************"<<"\n";
	spdout<<"OUTPUT FILES"<<"\n"<<"\n";
	
	
	spdout<<"The program will create a directory called \"[network.dat]_oslo_files\". If the directory is not empty it will cleared, so be careful if you want to save some previous output files.\n"<<"\n";
	spdout<<"All the files will be written in this directory. "<<"\n";
	spdout<<"The first level partition will be written in a file called \"tp\", the next ";
	spdout<<"hierchical network will be recorded as \"net1\", "<<"\n";
	spdout<<"the second level partition will be called \"tp1\" and so on."<<"\n";
	spdout<<"For convenience, the first level partition will be also written in a file called \"tp\" located in the same folder where the program is."<<"\n";
	spdout<<"***************************************************************************************************************************************************"<<"\n";
	
	
	spdout<<"\n"<<"\n";
	spdout<<"PLEASE LOOK AT ReadMe.pdf for more details. Thanks!"<<"\n"<<"\n"<<"\n";
	
	
	
}




void error_statement(char * b) {

	cerr<<"\n\n************************************************************"<<"\n";
	cerr<<"ERROR while reading parameters from command line... Please read program instructions or type: \n"<<b<<"\n";
	cerr<<"************************************************************"<<"\n";


}





Parameters::~Parameters(){};

void Parameters::print() {
	
	
	spdout<<"**************************************"<<"\n";
	spdout<<"Threshold:\t\t\t"<<threshold<<"\n";
	spdout<<"Network file:\t\t\t"<<file1<<"\n";
	
	
	if(weighted)
		spdout<<"Weighted: yes"<<"\n";
	else
		spdout<<"Weighted: no"<<"\n";

	if(fast)
		spdout<<"-fast option selected"<<"\n";
		
	if(value)
		spdout<<"Hint from file:\t\t\t"<<file2<<"\n";
	if(value_load)
		spdout<<"tp-file:\t\t\t"<<file_load<<"\n";

	spdout<<"First Level Runs:\t\t\t"<<Or<<"\n";
	spdout<<"Higher Level Runs:\t\t\t"<<hier_gather_runs<<"\n";
	spdout<<"-cp:\t\t\t"<<coverage_percentage_fusion_or_submodules<<"\n";
	
	if(seed_random!=-1)
		spdout<<"Random number generator seed:\t\t\t"<<seed_random<<"\n";
	
	if(homeless_anyway==false)
		spdout<<"-singlet option selected"<<"\n";
	
	
	for(UI i=0; i<to_run.size(); i++)
		spdout<<"String to run: ["<<to_run[i]<<"]\t\t\t\t\t\tModule file: ["<<to_run_part[i]<<"]"<<"\n";
	
	
	spdout<<"**************************************"<<"\n"<<"\n";
	
	
	
	
	
}



bool Parameters::set_flag_and_number(double & number_to_set, int & argct, int argc, char * argv[], double min_v, double max_v, string warning) {
	
	argct++;
	if(argct==argc) {
		
		spdout<<"you didn't set any number for the "<<warning<<"\n";
		error_statement(argv[0]);
		return false;
	}
	
	string tt=argv[argct];
	double ttt;
	if(cast_string_to_double(tt, ttt)==false) {
	
		spdout<<"you didn't set any number for the "<<warning<<"\n";	
		error_statement(argv[0]);
		return false;
	}
	
	number_to_set=ttt;
	
	if(number_to_set<min_v || number_to_set>max_v) {	
		spdout<<"the "<<warning<<" must be between "<<min_v<<" and "<<max_v<<"\n";
		error_statement(argv[0]);
		return false;
	}
		
	return true;
}



bool Parameters::set_flag_and_number(int & number_to_set, int & argct, int argc, char * argv[], int min_v, int max_v, string warning) {
	
	argct++;
	if(argct==argc) {
		
		spdout<<"you didn't set any number for the "<<warning<<"\n";
		error_statement(argv[0]);
		return false;
	}
	
	string tt=argv[argct];
	double ttt;
	if(cast_string_to_double(tt, ttt)==false) {
	
		spdout<<"you didn't set any number for the "<<warning<<"\n";	
		error_statement(argv[0]);
		return false;
	}
	
	number_to_set=cast_int(ttt);
	
	if(number_to_set<min_v || number_to_set>max_v) {	
		spdout<<"the "<<warning<<" must be between "<<min_v<<" and "<<max_v<<"\n";
		error_statement(argv[0]);
		return false;
	}
		
	return true;
	
	
	
}









Parameters::Parameters() {
	
	//**************************************************************************
	
	
	
	seed_random=-1;	
	
	threshold= 0.1;											// this is the P-value for the significance of the module
	
	clean_up_runs=25;										// the number of runs in the clean up procedure
	inflate_runs=3;											// the number of runs in the clean up of the inflate procedure
	inflate_stopper=5;										// the number of runs in the inflate procedure
	equivalence_parameter=0.33;								// this parameters tells when nodes are considered equivalent in the clean up procedure
	CUT_Off=200;											// this is used in the inflate function
	
	maxborder_nodes=100;									// this is to speed up the code in looking for "reasonably good" neighbors
	maxbg_ordinary=0.1;										// same as above
	iterative_stopper=10;									// this is to prevent the iterative procedure to last too long. this can happen in case of strong backbones (just an idea, not sure)
	minimality_stopper=10;									// this is to prevent too many minimality checks
	hierarchy_convergence=0.05;								// this parameter is used to stop the hierarchical process when not enough modules are found
	
	Or=10;													// this is the number of global runs in the gather function		(first level)
	hier_gather_runs=50;									// this is the number of global runs in the gather function		(higher level)
	
	coverage_inclusion_module_collection=0.49999;			// this is used to see if two modules are higly similar in processing the clusters (big_module)
	coverage_percentage_fusion_left=0.8;					// this is used to see when fusing clusters how much is left
	check_inter_p=0.05;										// this parameter is a check parameter for the fusion of quite similar clusters
	coverage_percentage_fusion_or_submodules=0.5;			// this is the resolution parameter to decide between split clusters or unions, if you increase this value the program tends to find bigger clusters 
		
	
	print_flag_subgraph=true;										// this flag is used to print things when necessary
	
	/* these are some flags to read input files */
	value=false;
	value_load=false;		
	fast=false;
	weighted=false;
	homeless_anyway=true;


	//********************* collect_groups	
	max_iteration_convergence=10;							// parameter for the convergence of the collect_groups function
	
	
	
	infomap_runs=0;
	copra_runs=0;
	louvain_runs=0;
	
	
	
	
	
	command_flags.insert(make_pair("-w", 1));
	command_flags.insert(make_pair("-uw", 2));
	command_flags.insert(make_pair("-singlet", 3));	
	command_flags.insert(make_pair("-f", 4));
	command_flags.insert(make_pair("-hint", 5));
	command_flags.insert(make_pair("-load", 6));
	command_flags.insert(make_pair("-t", 7));
	command_flags.insert(make_pair("-r", 8));
	command_flags.insert(make_pair("-hr", 9));
	command_flags.insert(make_pair("-seed", 10));
	command_flags.insert(make_pair("-cp", 11));
	command_flags.insert(make_pair("-fast", 12));
	command_flags.insert(make_pair("-infomap", 13));
	command_flags.insert(make_pair("-copra", 14));
	command_flags.insert(make_pair("-louvain", 15));
	
	
}








bool Parameters::set_flag_and_number_external_program(string program_name, int & argct, int & number_to_set, int argc, char * argv[]) {



	
	argct++;
	if(argct==argc) {
		
		spdout<<"you didn't set the number of "<<program_name<<"\n";
		
		error_statement(argv[0]);
		return false;
	}
	
	string tt=argv[argct];
	double ttt;
	if(cast_string_to_double(tt, ttt)==false) {
	
		spdout<<"you didn't set the number of "<<program_name<<"\n";

	
		error_statement(argv[0]);
		return false;
	}
	
	number_to_set=cast_int(ttt);
	
	if(number_to_set<0) {
	
		spdout<<" the number of "<<program_name<<" must be positive"<<"\n";

		error_statement(argv[0]);
		return false;
	}
	
	
	
	return true;
	
	
	
}








bool Parameters::_set_(int argc, char * argv[]) {
	
	int argct = 0;
	string temp;
	
	if (argc <= 1) {			/* if no arguments, return error_statement about program usage.*/
		
		error_statement(argv[0]);
		return false;
	}
	
	
	bool f_set=false;
	bool set_weighted=false;

	
	
	while (++argct < argc) {			// input file name
	
		
		spdout<<"setting "<<argv[argct]<<"\n";
		temp = argv[argct];
		map<string, int>::iterator itf=command_flags.find(temp);
		
		if(itf==command_flags.end()) {
			error_statement(argv[0]);
			return false;
		}
		
		int vp=itf->second;
		
		switch(vp) {
	
			case 1:
				weighted=true;
				set_weighted=true;
				break;
			case 2:
				weighted=false;
				set_weighted=true;
				break;
			case 3:
				homeless_anyway=false;
				break;
			case 4:
				argct++;
				if(argct==argc) {
					error_statement(argv[0]);
					return false;
				}
				file1=argv[argct];
				f_set=true;
				break;
			case 5:
				argct++;
				if(argct==argc) {
					error_statement(argv[0]);
					return false;
				}
				file2=argv[argct];
				value=true;
				break;
			case 6:
				argct++;
				if(argct==argc) {
					error_statement(argv[0]);
					return false;
				}
				file_load=argv[argct];
				value_load=true;
				break;
			case 7:
				if(set_flag_and_number(threshold, argct, argc, argv, 0., 1., "threshold")==false)
					return false;
				break;
			case 8:
				if(set_flag_and_number(Or, argct, argc, argv, 0, R2_IM2, "runs")==false)
					return false;
				break;
			case 9:
				if(set_flag_and_number(hier_gather_runs, argct, argc, argv, 0, R2_IM2, "higher-level runs")==false)
					return false;
				break;
			case 10:
				if(set_flag_and_number(seed_random, argct, argc, argv, 1, R2_IM2, "seed of the random number generator")==false)
					return false;
				break;
			case 11:
				if(set_flag_and_number(coverage_percentage_fusion_or_submodules, argct, argc, argv, 0., 1., "resolution parameter")==false)
					return false;
				break;
			case 12:
				fast=true;
				break;
			case 13:
				if(set_flag_and_number_external_program("runs for infomap", argct, infomap_runs, argc,  argv)==false)
					return false;
				break;
			case 14:
				if(set_flag_and_number_external_program("runs for copra", argct, copra_runs, argc,  argv)==false)
					return false;
				break;
			case 15:
				if(set_flag_and_number_external_program("runs for louvain method", argct, louvain_runs, argc,  argv)==false)
					return false;
				break;
			default:
				error_statement(argv[0]);
				return false;		
		}

	
	
	
	
	}
	
	/*******************************************************************/
	
	
	if(f_set==false) {
		
		cerr<<"\n\n************************************************************"<<"\n";
		spdout<<"ERROR: you didn't set the file with the network.  Please read program instructions or type: \n"<<argv[0]<<"\n";
		cerr<<"************************************************************"<<"\n";
		
		return false;
		
	}
	
	if(set_weighted==false) {	
		
		cerr<<"\n\n************************************************************"<<"\n";
		spdout<<"ERROR: you didn't set the option -w (weighted network) or -uw (unweighted network).  Please read program instructions or type: \n"<<argv[0]<<"\n";
		cerr<<"************************************************************"<<"\n";
		
		return false;
	}	
	
	if(seed_random==-1)
		srand_file();
	else
		srand5(seed_random);
	
	
	if(fast) {
		Or=1;
		hier_gather_runs=1;
	}
	
	
	
	
	
	for(int i=0; i<infomap_runs; i++) {
		
		char number_r[1000];
		
		//spdout<<"************** "<<string(argv[0])<<"\n";
		string pros(argv[0]);
		
		if(pros=="./oslom_undir")
			sprintf(number_r, "./infomap_undir_script NETx %d %d", irand(10000000), 1);
		else
			sprintf(number_r, "./infomap_dir_script NETx %d %d", irand(10000000), 1);
		
		string sr(number_r);
		
		//spdout<<"here "<<"\n";
		to_run.push_back(sr);
		to_run_part.push_back("infomap.part");
	
	}
	
	
	for(int i=0; i<copra_runs; i++) {
		
		char number_r[1000];
		sprintf(number_r, "java -cp copra.jar COPRA NETx -v 5 -w");			
		string sr(number_r);
		
		
		to_run.push_back(sr);
		to_run_part.push_back("clusters-NETx");
	
	}

		
	for(int i=0; i<louvain_runs; i++) {
		
		char number_r[1000];
		sprintf(number_r, "./louvain_script -f NETx");			
		string sr(number_r);
		
		
		to_run.push_back(sr);
		to_run_part.push_back("louvain.part");
	
	}

	
	
	

	
	return true;
}



}

