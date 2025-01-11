
#include "set_parameters.h"
#include "module_collection.h"

namespace oslom {
extern Parameters *paras;



module_collection::~module_collection(){};

		int module_collection::size() { return module_bs.size(); };
		


module_collection::module_collection(int dim) {

	_set_(dim);
}


void module_collection::_set_(int dim) {

	
	set<int> first;
	for(int i=0; i<dim; i++)
		memberships.push_back(first);
	
		


}



bool module_collection::insert(deque<int> & c, double bs) {


	int new_name;
	return insert(c, bs, new_name);
	
}




bool module_collection::insert(deque<int> & c, double bs, int & new_name) {

	
	if(bs==0)
		bs=ran4() * 1e-100;
	
	
	sort(c.begin(), c.end());
	new_name=-1;
	
	if(check_already(c)==true) {	
		
		new_name=modules.size();
		for(int i=0; i<int(c.size()); i++)
			memberships[c[i]].insert(new_name);	
		
		
		modules.push_back(c);
		module_bs[new_name]=bs;
		
		
		return true;
		
	}
	
	return false;
	
}





bool module_collection::erase(int a) {
	
	// it erases module a 
	
	
	
	if(module_bs.find(a)==module_bs.end())		// it only erases not empty modules
		return false;
	
	deque<int> & nodes_a = modules[a];
	
	for(int i=0; i<int(nodes_a.size()); i++)
		memberships[nodes_a[i]].erase(a); 
	
			
	modules[a].clear();
	module_bs.erase(a);
	
	
	
	return true;

}











void module_collection::print(ostream & outt, deque<int> & netlabels, bool not_homeless) {
	
	
		
	
	int nmod=0;
	for(map<int, double >::iterator itm = module_bs.begin(); itm!=module_bs.end(); itm++) if(not_homeless==false || modules[itm->first].size() > 1) {
		
		
		nmod++;
		
		
		deque<int> & module_nodes= modules[itm->first];
		outt<<"#module "<<itm->first<<" size: "<<modules[itm->first].size()<<" bs: "<<module_bs[itm->first]<<"\n";
		
		deque<int> labseq;
		for(int i=0; i<int(module_nodes.size()); i++) {
			labseq.push_back(netlabels[module_nodes[i]]);
		}
		
		sort(labseq.begin(), labseq.end());
		
		for(int i=0; i<int(labseq.size()); i++) {
			outt<<labseq[i]<<" ";
		}
		outt<<"\n";
		
		

	}
	
	

}





void module_collection::fill_gaps() {

	for(int i=0; i<int(memberships.size()); i++)
		if(memberships[i].size()==0) {
			
			deque<int> new_d;
			new_d.push_back(i);
			insert(new_d, 1.);
			
		
		}

}



void module_collection::put_gaps() {
		
	deque<int> to_erase;
	
	
	for(int i=0; i<int(modules.size()); i++) {
		
		if(modules[i].size()==1)
			to_erase.push_back(i);
	}
	
	
	for(int i=0; i<int(to_erase.size()); i++)
		erase(to_erase[i]);
	
}



//*/



void module_collection::homeless(deque<int> & h) {
	
	h.clear();
	
	for(int i=0; i<int(memberships.size()); i++)
		if(memberships[i].size()<1)
			h.push_back(i);
	
	for(int i=0; i<int(modules.size()); i++) {
		
		if(modules[i].size()==1)
			h.push_back(modules[i][0]);
	
	}
	
	
	sort(h.begin(), h.end());
		

}


int module_collection::coverage() {
	
	
	// this function returns the number of nodes which are covered by at least one module
	
	int cov=0;
	for(int i=0; i<int(memberships.size()); i++)
		if(memberships[i].size()>0)
			cov++;
	
	
	
	return cov;


}



int module_collection::effective_groups() {
	
	
	
	int nmod=0;
	for(map<int, double >::iterator itm = module_bs.begin(); itm!=module_bs.end(); itm++) if(modules[itm->first].size() > 1)		
		nmod++;
	
	return nmod;
	
	
	
}






void module_collection::set_partition(deque<deque<int> > & A) {

	A.clear();

	for(map<int, double >::iterator itm = module_bs.begin(); itm!=module_bs.end(); itm++) if(modules[itm->first].size()>1)
		A.push_back(modules[itm->first]);
}


void module_collection::set_partition(deque<deque<int> > & A, deque<double> & b) {


	A.clear();
	b.clear();
	
	for(map<int, double>::iterator itm = module_bs.begin(); itm!=module_bs.end(); itm++) if(modules[itm->first].size()>1){
		A.push_back(modules[itm->first]);
		b.push_back(module_bs[itm->first]);
	}





}






bool module_collection::check_already(const deque<int> & c) {

	// returns false if the module is already present
	
	
	
	map<int, int> com_ol;		// it maps the index of the modules into the overlap (overlap=numeber of overlapping nodes)
	
	for(int i=0; i<int(c.size()); i++) {
		
		for(set<int>:: iterator itj=memberships[c[i]].begin(); itj!=memberships[c[i]].end(); itj++)
			int_histogram(*itj, com_ol);
		
	
	}
	
	
	
	for(map<int, int>::iterator itm=com_ol.begin(); itm!=com_ol.end(); itm++) {
		
		if(itm->second==int(c.size()) && itm->second==int(modules[itm->first].size()))
			return false;
			
	}
	
		
	return true;



}





void module_collection::compute_inclusions() {

	put_gaps();
	erase_included();
	compact();
	
}



void module_collection::erase_included() {


	map<int, deque<int> > erase_net;
	for(map<int, double >::iterator itm= module_bs.begin();  itm!=module_bs.end(); itm++) {
	

		deque<int> smaller;
		almost_equal(itm->first, smaller);
		erase_net[itm->first]=smaller;	
	
	}
	
	while(true) {
		
		if(erase_first_shell(erase_net)==false)
			break;

	}


}





bool module_collection::erase_first_shell(map<int, deque<int> > & erase_net) {
	

	bool again=false;
	set<int> roots;
	
	for(map<int, double >::iterator itm= module_bs.begin();  itm!=module_bs.end(); itm++)
		roots.insert(itm->first);

	
	
	
	for(map<int, deque<int> >::iterator itm= erase_net.begin();  itm!=erase_net.end(); itm++) {
	

		deque<int> & smaller=itm->second;
		
		for(int i=0; i<int(smaller.size()); i++)
			roots.erase(smaller[i]);
	
	}
	
	
	//spdout<<"roots:"<<"\n";
	//prints(roots);
	


	for(set<int>::iterator its=roots.begin(); its!=roots.end(); its++) {
		
		deque<int> & smaller=erase_net[*its];
		
		
		for(int i=0; i<int(smaller.size()); i++) {
		
			if(module_bs.find(smaller[i])!=module_bs.end()) {
				
				erase(smaller[i]);
				erase_net.erase(smaller[i]);
				again=true;
			
			}
		}
		
	}

	
	return again;

}







bool module_collection::almost_equal(int module_id, deque<int> & smaller) {

	// c is the module you want to know about
	// smaller is set to contain the module ids contained by module_id
	
	smaller.clear();
	
	deque<int> & c= modules[module_id];
	
	map<int, int> com_ol;		// it maps the index of the modules into the overlap (overlap=numeber of overlapping nodes)
	
	for(int i=0; i<int(c.size()); i++) {
		
		for(set<int>:: iterator itj=memberships[c[i]].begin(); itj!=memberships[c[i]].end(); itj++)
			int_histogram(*itj, com_ol);
	
	}
	
	
	
	for(map<int, int>::iterator itm=com_ol.begin(); itm!=com_ol.end(); itm++) if(itm->first!=module_id && modules[itm->first].size()<= c.size()) {

		const UI & other_size= modules[itm->first].size();
			
		if(double(itm->second) / other_size >= paras->coverage_inclusion_module_collection) {

			if(c.size() > other_size)
				smaller.push_back(itm->first);
			else if(c.size()==other_size && module_bs[module_id]<module_bs[itm->first])
				smaller.push_back(itm->first);			
		}
		
			
	}
	
	
	return true;

}





void module_collection::compact() {
	
	
	/* this function is used to have continuos ids */
	
	put_gaps();
	
		
	map<int, int> from_old_index_to_new;


	{
		
		deque<deque<int> > modules2;
		map<int, double> module_bs2;
	
	
		for(map<int, double> :: iterator itm= module_bs.begin(); itm!=module_bs.end(); itm++) {
			from_old_index_to_new.insert(make_pair(itm->first, from_old_index_to_new.size()));
			modules2.push_back(modules[itm->first]);
			module_bs2[from_old_index_to_new.size()-1]=itm->second;
		}
		
		
		modules=modules2;
		module_bs=module_bs2;
	}
	
	
	
	
	for(UI i=0; i<memberships.size(); i++) {
		
		set<int> first;
		for(set<int>:: iterator its= memberships[i].begin(); its!=memberships[i].end(); its++)
			first.insert(from_old_index_to_new[*its]);
		
		memberships[i]=first;
	}
	
	


	
}


void module_collection::sort_modules(deque<int> & module_order) {

	module_order.clear();
	multimap<double, int> rank_id;		/* modules are sorted from the biggest to the smallest. if they have equal size, we look at the score */
		
	for(map<int, double >::iterator itm = module_bs.begin(); itm!=module_bs.end(); itm++) {
		
		//spdout<<modules[itm->first].size()<<" ... "<<"\n";
		rank_id.insert(make_pair(-double(modules[itm->first].size()) + 1e-2 * itm->second, itm->first));
	
	}
	//spdout<<"rank_id"<<"\n";
	//prints(rank_id);
	for(multimap<double, int >::iterator itm = rank_id.begin(); itm!=rank_id.end(); itm++)
		module_order.push_back(itm->second);

}





bool module_collection::egomodules_to_merge(deque<int> & egom, deque<int> & smaller) {
	
	// egom is the module you want to know about
	// smaller is set to contain the module ids to merge with egom
	
	smaller.clear();
	
	
	map<int, int> com_ol;		// it maps the index of the modules into the overlap (overlap=numeber of overlapping nodes)
	
	for(int i=0; i<int(egom.size()); i++) {
		
		for(set<int>:: iterator itj=memberships[egom[i]].begin(); itj!=memberships[egom[i]].end(); itj++)
			int_histogram(*itj, com_ol);
		
	}
	
	
	//spdout<<"egomodules_to_merge"<<"\n";
	//prints(egom);
	
	for(map<int, int>::iterator itm=com_ol.begin(); itm!=com_ol.end(); itm++) {
		
		
		//spdout<<" other group "<<itm->second<<"\n";
		//prints(modules[itm->first]);
		
		const UI & other_size= min(modules[itm->first].size(), egom.size());
		if(double(itm->second) / other_size >= paras->coverage_inclusion_module_collection)
			smaller.push_back(itm->first);
	}
	
	
	return true;
	
}

void module_collection::merge(DI & c) {

	DI to_merge;
	egomodules_to_merge(c, to_merge);
	
	//spdout<<"module c: "<<"\n";
	//prints(c);
	
	if(to_merge.size()==0)
		insert(c, 1.);
	else {
		for(UI i=0; i<to_merge.size(); i++) {
			
			
			//spdout<<"to_merge"<<"\n";
			//prints(modules[to_merge[i]]);
			
			
			set<int> si;
			deque_to_set_app(modules[to_merge[i]], si);
			deque_to_set_app(c, si);
			erase(to_merge[i]);
			
			//prints(si);
			
			
			DI to_insert;
			set_to_deque(si, to_insert);
			insert(to_insert, 1.);
			
		
		}
	}
	
	
	erase_included();

}


}
