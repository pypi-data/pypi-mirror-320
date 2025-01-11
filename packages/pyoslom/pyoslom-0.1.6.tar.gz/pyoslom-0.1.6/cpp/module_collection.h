

#ifndef module_collection_INCLUDED
#define module_collection_INCLUDED

#include "standard_package/standard_include.h"


namespace oslom {


class module_collection {		

	/* all the labels refers to the index in int_matrix modules */

	
	public:
	
		module_collection(int d);
		~module_collection();

		int size();
		
		bool insert(deque<int> & c, double bs, int & new_name);
		bool insert(deque<int> & c, double bs);
		bool erase(int);			
		void print(ostream & outt, deque<int> & netlabels, bool);		
		
		void fill_gaps();
		void put_gaps();
		void homeless(deque<int> & h);
		int coverage();
		int effective_groups();

		void set_partition(deque<deque<int> > & A);
		void set_partition(deque<deque<int> > & A, deque<double> & b);
	
		void compute_inclusions();
		void erase_included();
		bool almost_equal(int module_id, deque<int> & smaller);

		void compact();
		void sort_modules(DI &);
		void merge(DI & c);
		
		/*************************** DATA ***************************/
		
		
		deque<set<int> > memberships;					
		int_matrix modules;		
		map<int, double> module_bs;						/* it maps the module id into the b-score */
		
		/***********************************************************/

	private:
		
		void _set_(int dim);
		bool check_already(const deque<int> & c);
		bool erase_first_shell(map<int, deque<int> > & erase_net);
		bool egomodules_to_merge(deque<int> & egom, deque<int> & smaller);

};



}

#endif
