/*
	Author: Rafael Kendy Arakaki
	Advisor: Prof. Fábio Luiz Usberti
    Institute of Computing - University of Campinas, Brazil

	Title: Hybrid Genetic Algorithm for the OCARP (Open Capacitated Arc Routing Problem)
    Description: A genetic algorithm hybridized with feasibilization and local search routines.
    This algorithm works with a chromosome that represents a non-capacitated route (we call it non-capacitataed chromosome). Solutions are obtained through Split procedure.
    The feasibilization routine uses the Split algorithm to achieve OCARP solutions. When the Split fails, good routes regarding capacity usage are fixed into the solution, thus improving the chance to make a feasible solution.
    The local search uses a deconstruct/reconstruct approach that improves the solution cost by deconstructing and reconstructing some of the routes of an OCARP solution.
	The local search also takes advantage from the Split algorithm.
*/

// Final version 1.0
#include "hga.h"

// Instance data
int nTasks;
int nNodes, nEdges;
int nReqEdges;
int maxroutes;
int capacity;

// Instance parameters
int LIMITE_TEMPO = 3600;
int M_plus;

// GA parameters
int POP;
double LOCALSEARCH_FILTER_MULTIPLIER = 2.0;
int RESTART_INTERVAL = 150;

// Graph Data
ListGraph *g = new ListGraph;
ListGraph::EdgeMap<int> *custoAresta;
ListGraph::EdgeMap<int> *demandaAresta;
vector<vector<int> > spG; // Shortest path between arcs

// Tasks Data (tasks == required arcs)
map<int, ListGraph::Edge> edgeFromTask;
map<int, int> custo;
map<int, int> demanda;
int **D = NULL;

// GA Populations
Population pop1, pop2;
Population *current_population;
Population *other_population;

// Local search stochastic filter
vector<int> filterSampleBefore;
vector<int> filterSampleAfter;
double filterMean;
double filterStdDeviation;

// Best solution (output)
Solution bestSolution;
int bestCost;
int bestCostGeneration;
clock_t bestSolutionClock;

// Experiments data
int lb0_value;
char strname[100];

// Statistics
int recursoesFactivel[100];
double allInstances_mediaBestRatio = 0.0;
int counterInstances;
int passLS, failLS;
int numSolsFactiveis = 0, numSolsInfactiveis = 0;

// Output files
FILE* resultsLatex;
FILE* resultsCalc;

// Usage information
void showUsage (){
    cout << "Usage: ./ga <#Vehicles M*+(0/1/2)> {-t <time_limit> (seconds)} {-r: restart interval (# generations)} "
    << "{-u: local search filter multiplier (* stdev)}" << endl;
}

int main(int argc, char *argv[]) {
    cout << "------------" << endl << "HGA-OCARP" << endl
    << "Version: 1.0" << endl << "------------"
    << endl << endl;

    // Input arguments checking
    if (argc < 2) {
        cout << "Parameters missing." << endl;
        showUsage();
        exit(1);
    }

    M_plus = atoi(argv[1]);
    if (M_plus < 0) {
        cout << "Parameter <#Vehicles M*+(0/1/2)> invalid. Must be >= 0" << endl;
        exit(1);
    }

    // Reading program arguments
    for(int i = 2; i < argc; i++){
        const string arg(argv[i]);
        string next;
        if((i+1) < argc)
            next = string(argv[i+1]);
        else
            next = string("");

        if( arg.find("-t") == 0 && next.size() > 0){
            LIMITE_TEMPO = atoi(next.c_str()); i++; continue;
        }
        else if( arg.find("-r") == 0 && next.size() > 0){
            RESTART_INTERVAL = atoi(next.c_str()); i++; continue;
        }
        else if( arg.find("-u") == 0 && next.size() > 0){
            LOCALSEARCH_FILTER_MULTIPLIER = atof(next.c_str()); i++; continue;
        }
        else{
            cout << "Invalid parameter: \"" << arg << "\"" << "" << endl;
            showUsage();
            exit(1);
        }
    }

    cout << "*** HGA-OCARP STARTING *** " << endl << "-----------------------------------" << endl << "PARAMETERS:" << endl;

    cout << "NUM_VEHICLES_PLUS: " << M_plus << endl;
    cout << "TIME_LIMIT: " << LIMITE_TEMPO << endl;
    cout << "POP_SIZE: " << POP_SIZE << endl;
    cout << "MAX_ALPHA_RCL: " << MAX_ALPHA_RCL << endl;
    cout << "LOCAL_SEARCH: " << "MEAN + " << LOCALSEARCH_FILTER_MULTIPLIER << " * STD-DEVIATION" << endl;
    cout << "RESTART_INTERVAL: " << RESTART_INTERVAL << endl;
    cout << "RESTART_POPULATION_NUM: " << RESTART_POPULATION_NUM << endl;
    cout << "RESTART_POPULATION_BEST_PRESERVE: " << RESTART_POPULATION_BEST_PRESERVE << endl;

    cout << "---------------------------------------------------" << endl;

    // Output preparation
    char latexstr[100], calcstr[100];
    sprintf(latexstr, "results_latex_%d.txt", M_plus);
    sprintf(calcstr, "results_calc_M%d.txt", M_plus);
    resultsLatex = fopen(latexstr, "w");
    resultsCalc =  fopen(calcstr, "w");
    fprintf(resultsLatex, "<instance> &\t<M*> &\t<LB> &\t<UB> &\t<GAP(%%)> &\t<FEAS(%%)> &\t<CPU>\n" );
    fprintf(resultsCalc,  "<instance> \t<M*> \t<LB> \t<UB> \t<GAP(%%)> \t<FEAS(%%)> \t<CPU>\n" );

    // Instance list
    FILE *lista = fopen("./instancias-OCARP/instancias.txt", "r");
    if(lista == NULL){
        cout << "Instance list file not found." << endl;
        exit(1);
    }
    fscanf(lista, " %s", strname);
    counterInstances = 0;
    while (strcmp(strname, "END") != 0) {
        // Find next instance
        printf("Instancia %s:\n", strname);
        char filepath[100];
        sprintf(filepath, "./instancias-OCARP/%s", strname);
        std::string sfile(filepath);

        // Allocate instance objects
        g = new ListGraph;
        custoAresta = new ListGraph::EdgeMap<int>(*g);
        demandaAresta = new ListGraph::EdgeMap<int>(*g);

        // Instance reading
        readFile(sfile, *g, *custoAresta, *demandaAresta);

        // Check limits
        if (nReqEdges > GENE_SIZE) {
            printf("***ERRO***: Chromosome size too short (%d). Please increase GENE_SIZE.", GENE_SIZE);
            exit(1);
        }

        // Pre-processing (shortest path matrix between required arcs)
        pre_processamento();

        // Genetic Algorithm
        genetic_algorithm();

        // Memory deallocation
        for (int i = 1; i <= nTasks; i++){
            delete[] D[i];
        }
        delete[] D;
        nTasks = nNodes = nEdges = nReqEdges = 0;
        delete custoAresta;
        delete demandaAresta;
        delete g;
        edgeFromTask.clear();
        custo.clear();
        demanda.clear();
        filterSampleBefore.clear();
        filterSampleAfter.clear();
        numSolsFactiveis = numSolsInfactiveis = 0;

        
        // Next instance
        counterInstances++;
        fscanf(lista, " %s", strname);
        fflush(resultsLatex); fflush(resultsCalc);
    }
    fclose(lista);

    // Statistics
    allInstances_mediaBestRatio /= counterInstances;
    printf("GAP from lb_0 average (of all %d instances): %.3f\n", counterInstances, allInstances_mediaBestRatio);
    fprintf(resultsLatex, "GAP from lb_0 average (of all %d instances): %.3f\n", counterInstances, allInstances_mediaBestRatio);
    fprintf(resultsCalc,  "GAP from lb_0 average (of all %d instances): %.3f\n", counterInstances, allInstances_mediaBestRatio);

    printf("***HGA-OCARP EXITING***\n");

    fclose(resultsLatex);
    fclose(resultsCalc);
    return 0;
}

// HGA primary function
void genetic_algorithm() {
    // Input: nTasks, D: nTasks x nTasks
    current_population = &pop1;
    other_population = &pop2;
    bestCost = INT_MAX;
    bestCostGeneration = 0;

    // Population clear
    pop1.ordered.clear();
    pop2.ordered.clear();

    // Population init
    clock_t begin = clock();
    inicializar_populacao();

    // Output solution file
    char strout[100];
    sprintf(strout, "./resultados_M%d/%s.txt", M_plus, strname);

    // Checks if any optimal solution was found
    if (bestCost == lb0_value){
        PRINTF("BestCost from init   = %d (gap %.2f) TimeSpent=%.1fs.\n", bestCost, (double) 100.0 * (bestCost - lb0_value) / lb0_value, double(clock() - begin) / CLOCKS_PER_SEC);
        allInstances_mediaBestRatio += 0.000;
        fprintf(resultsLatex, "%s &\t %d &\t %d &\t %d &\t %.2lf &\t %.2lf &\t %.1lf\n", strname, maxroutes-M_plus, lb0_value, bestCost, (double) 100.0 * (bestCost - lb0_value) / lb0_value, (100.0*numSolsFactiveis/(numSolsFactiveis+numSolsInfactiveis)), double(bestSolutionClock - begin) / CLOCKS_PER_SEC);
        fprintf(resultsCalc,  "%s \t %d \t %d \t %d \t %.2lf \t %.2lf \t %.1lf\n", strname, maxroutes-M_plus, lb0_value, bestCost, (double) 100.0 * (bestCost - lb0_value) / lb0_value, (100.0*numSolsFactiveis/(numSolsFactiveis+numSolsInfactiveis)), double(bestSolutionClock - begin) / CLOCKS_PER_SEC);
        writeSolution(strout, bestSolution);
        return;
    }
    else{
        PRINTF("BestCost from init   = %d (gap %.2f) TimeSpent=%.1fs.\n", bestCost, (double) 100.0 * (bestCost - lb0_value) / lb0_value, double(clock() - begin) / CLOCKS_PER_SEC);
    }

    // HGA main body
    double cpu_secs = 0.0;
    int k = 0;
    int kNotImproved = 0;
    double lastBestCost = 0;
    passLS = 0; failLS = 0;
    while ( cpu_secs < LIMITE_TEMPO ) {
        // Population ordering from fitness
        current_population->ordered.clear();
        for (int p = 0; p < POP; p++) {
            current_population->ordered.insert(pair<int, int>(current_population->obj_value[p], p));
        }

        // Population selection
        vector<int> sobreviventes;
        for(auto ele : current_population->ordered){
            sobreviventes.push_back(ele.second);
        }
        random_shuffle(sobreviventes.begin()+1, sobreviventes.end()); // The best solution is never replaced

        // Crossover Selection
        vector<int> crossoverSelected;
        const int quantFilhos = POP-1;
        const int quantPais = quantFilhos*2;

        // Parents selection from SUS (Stochastic Universal Sampling from Baker)
        // Baker, James E. (1987). "Reducing Bias and Inefficiency in the Selection Algorithm". Proceedings of the Second International Conference on Genetic Algorithms and their Application.
        // https://en.wikipedia.org/wiki/Stochastic_universal_sampling
        selectCrossover(crossoverSelected, quantPais);

        // Parents shuffle
        random_shuffle(crossoverSelected.begin(), crossoverSelected.end());

        // Crossover
        int newIdx = 0;
        for (int p = 0; p < quantPais; p += 2) {
            int pai1 = crossoverSelected[p], pai2 = crossoverSelected[p + 1];
            int filho[nReqEdges];
            if (irandom(1) == 0)
                crossover(pai1, pai2, filho);
            else
                crossover(pai2, pai1, filho);

            // Feasibilization routine
            vector<vector<int> > solucao;
            bool factivel = factibilizar_dificil(filho, nReqEdges, maxroutes, solucao);
            if (factivel) {

                // Local Search
                vector<vector<int> > solutionLS = solucao;
                int custoBefore = objective_function(solucao);
                int custoAfter;

                // Stochastic Filter (bad solutions don't go to local search)
                if (filterSampleBefore.size() < STATISTICAL_FILTER_SAMPLE_SIZE || ((double) custoBefore/bestCost) < filterMean+ LOCALSEARCH_FILTER_MULTIPLIER*filterStdDeviation) {
					custoAfter = local_search_OCARP(solutionLS);

                    if( filterSampleBefore.size() < STATISTICAL_FILTER_SAMPLE_SIZE ){
                        filterSampleBefore.push_back(custoBefore);
                        filterSampleAfter.push_back(custoAfter);
                        if( filterSampleBefore.size() == STATISTICAL_FILTER_SAMPLE_SIZE ){
                            //cout << "*** STATISTICAL FILTER INITIALIZATION ***" << endl;
                            vector<double> vecRatios;
                            // Initial ratios "Sol_ini / Sol_ls" computation
                            for(int i = 0; i < filterSampleBefore.size(); i++){
                                double ratio = ((double) filterSampleBefore[i])/filterSampleAfter[i];
                                vecRatios.push_back(ratio);
                            }

                            // Calculates the average and standard deviation from ratios
                            double sum = std::accumulate(std::begin(vecRatios), std::end(vecRatios), 0.0);
                            filterMean = sum / vecRatios.size(); // average

                            double accum = 0.0;
                            std::for_each (std::begin(vecRatios), std::end(vecRatios), [&](const double d) {
                                accum += (d - filterMean) * (d - filterMean);
                            });

                            filterStdDeviation = sqrt(accum / (vecRatios.size()-1)); // "sample" standard deviation (Bessel's correction)
                            //cout << "- media: " << filterMean << ", stdev: " << filterStdDeviation << endl << endl;
                        }
                    }
                    else{
                        passLS++;
                        //cout << "Passou no filtro! ratio=" << ((double) custoBefore/bestCost) << " less than " << filterMean+2*filterStdDeviation << endl;
                    }
                }
                else {
					// No local search
                    solutionLS = solucao;
					custoAfter = custoBefore;
                    failLS++;
                    //cout << "NAO passou no filtro! ratio=" << ((double) custoBefore/bestCost) << " MORE THAN " << filterMean+2*filterStdDeviation << endl;
                }

                // Adiciona solução à nova população
                other_population->individual[newIdx].solucao = solutionLS;
                routes2noncapacitated_route(other_population->individual[newIdx].gene, solutionLS);
                other_population->obj_value[newIdx] = custoAfter;
                if (custoAfter < bestCost) {
                    bestCost = custoAfter;
                    bestCostGeneration = k;
                    bestSolution = other_population->individual[newIdx];
                    bestSolutionClock = clock();
                    if (lb0_value == custoAfter) {
                        clock_t end = clock();
                        cpu_secs = double(end - begin) / CLOCKS_PER_SEC;
                        cout << "Best final solution = " << bestCost << " (ratio: " <<
                        100.0 * ((double) bestCost - lb0_value) / lb0_value << "). (generations: " << k << ")." <<
                        " Time " << cpu_secs << " secs" << ". FilterPass(\%)= " << (100.0*passLS/(passLS+failLS)) << endl;
                        allInstances_mediaBestRatio += 0.000;
        fprintf(resultsLatex, "%s &\t %d &\t %d &\t %d &\t %.2lf &\t %.2lf &\t %.1lf\n", strname, maxroutes-M_plus, lb0_value, bestCost, (double) 100.0 * (bestCost - lb0_value) / lb0_value, (100.0*numSolsFactiveis/(numSolsFactiveis+numSolsInfactiveis)), double(bestSolutionClock - begin) / CLOCKS_PER_SEC);
        fprintf(resultsCalc,  "%s \t %d \t %d \t %d \t %.2lf \t %.2lf \t %.1lf\n", strname, maxroutes-M_plus, lb0_value, bestCost, (double) 100.0 * (bestCost - lb0_value) / lb0_value, (100.0*numSolsFactiveis/(numSolsFactiveis+numSolsInfactiveis)), double(bestSolutionClock - begin) / CLOCKS_PER_SEC);
                        writeSolution(strout, bestSolution);
                        return;
                    }
                    else {
                        //printf("Uma nova melhor solucao foi encontrada ! %d (ratio: %.2f) \n", bestCost, 100.0*((double)bestCost-lb0_value)/lb0_value);
                    }
                }
                other_population->fitness[newIdx] = (CONST_FITNESS_DIV * (double) 1) / (custoAfter - lb0_value);
                numSolsFactiveis++;
                newIdx++;
            }
            else{
                numSolsInfactiveis++;
            }
        }

        // Transfer individuals to new population
        int a = 0;
        for(; newIdx < POP; newIdx++){
            other_population->individual[newIdx] = current_population->individual[sobreviventes.at(a)];
            other_population->obj_value[newIdx] = current_population->obj_value[sobreviventes.at(a)];
            other_population->fitness[newIdx] = current_population->fitness[sobreviventes.at(a)];
            //PRINTF("Salva a solucao %d para nova populacao (custo=%d).\n", sobreviventes.at(k), current_population->obj_value[sobreviventes.at(k)]);
            a++;
        }

        // Population switch
        if(current_population == &pop1){
            current_population = &pop2;
            other_population = &pop1;
        }
        else{
            current_population = &pop1;
            other_population = &pop2;
        }

        // Population restart
        if( k > 0 && k % RESTART_INTERVAL == 0){
            restart_populacao();
        }

        // Get some statistics from the population after restarting
//        double media = 0.0;
//        for (int p = 0; p < POP; p++) {
//            media += current_population->obj_value[p];
//        }
//        if(k > 0 && k % RESTART_INTERVAL == 0) printf("Geracao %d: Media = %.2f (ratio: %.2f)\n", k, media/POP, 100.0*((media/POP)-lb0_value)/lb0_value);

        // Stop criteria
        if (bestCost == lastBestCost) {
            kNotImproved++;
        }
        else {
            kNotImproved = 0;
            lastBestCost = bestCost;
        }
        k++;
        clock_t end = clock();
        cpu_secs = double(end - begin) / CLOCKS_PER_SEC;
        //if(k % 1000 == 0) PRINTF("k = %d. BestCost = %d (Time: %.0fs)\n", k, bestCost, cpu_secs);
    }

    // Para verificar se a melhor solucao realmente está OK
    int verifyOK = objective_function(bestSolution.solucao);
    if (verifyOK != bestCost) {
        cout << "Error: reported cost from best solution != real cost. " << bestCost << " != " <<
        verifyOK << "..." << endl;
        cout << "sol has " << bestSolution.solucao.size() << " routes" << endl;
                //writeSolution("reportedBest.txt", bestSolution);
        exit(1);
    }
    else {
        cout << "Best final solution = " << bestCost << " (ratio: " <<
        100.0 * ((double) bestCost - lb0_value) / lb0_value << "). (generations: " << bestCostGeneration << " /" << k <<
        "). FeasibleSols=" << numSolsFactiveis <<". Feas(\%)= " << (100.0*numSolsFactiveis/(numSolsFactiveis+numSolsInfactiveis)) << ". Time " << (int) (double(bestSolutionClock - begin) / CLOCKS_PER_SEC) << " secs." << " FilterPass(\%)= " << (100.0*passLS/(passLS+failLS)) << endl;
        fprintf(resultsLatex, "%s &\t %d &\t %d &\t %d &\t %.2lf &\t %.2lf &\t %.1lf\n", strname, maxroutes-M_plus, lb0_value, bestCost, (double) 100.0 * (bestCost - lb0_value) / lb0_value, (100.0*numSolsFactiveis/(numSolsFactiveis+numSolsInfactiveis)), double(bestSolutionClock - begin) / CLOCKS_PER_SEC);
        fprintf(resultsCalc,  "%s \t %d \t %d \t %d \t %.2lf \t %.2lf \t %.1lf\n", strname, maxroutes-M_plus, lb0_value, bestCost, (double) 100.0 * (bestCost - lb0_value) / lb0_value, (100.0*numSolsFactiveis/(numSolsFactiveis+numSolsInfactiveis)), double(bestSolutionClock - begin) / CLOCKS_PER_SEC);
    }

    // Statistics
    writeSolution(strout, bestSolution);
    allInstances_mediaBestRatio += (double) 100.0 * (bestCost - lb0_value) / lb0_value;
    return;
}

// Random a integer random number in [0, a]
int irandom(int a) {
    if (a <= 0) return 0;
    else return rand() % (a + 1);
}

// Returns a float random number in [0,1].
double frandom() {
    return rand() / double(RAND_MAX);
}

// Calculates objective function (traversal cost) of a partial solution.
int obj_function_parcial(const vector<vector<int>> solution) {
    int cost = 0;
    set<int> conj;
    for (int r = 0; r < solution.size(); r++) {
        if( solution[r].size() > 0){
            int sum = 0, cap = 0;
            cap = demanda[solution[r][0]];
            sum = custo[solution[r][0]];
            if (conj.count(solution[r][0]) > 0) {
                printf("Error: Route %d contains a repeated task! (task: %d)\n", r,
                       solution[r][0]);
                int *a = 0;
                *a = 0;
                exit(1);
            }
            conj.insert(solution[r][0]);
            for (int i = 1; i < solution[r].size(); i++) {
                sum += sp(solution[r][i - 1], solution[r][i], D);
                int taskid = solution[r][i];
                //cout << taskid << "(" << nReqEdges << ")" << endl;
                cap += demanda[taskid];
                sum += custo[taskid];
                if (conj.count(solution[r][i]) > 0) {
                    printf("Error: Route %d contains a repeated task! (task: %d)\n", r,
                           solution[r][i]);
                    int *a = 0;
                    *a = 0;
                    exit(1);
                }
                conj.insert(solution[r][i]);
            }
            if (cap > capacity) {
                printf("Error: Capacity exceed in the route (index = %d)\n", r);
                exit(1);
            }
            cost += sum;
        }
    }

    // Nao da para verificar integridade de conj() aqui porque este metodo é parcial.
    return cost;
}

// Calculates objective function (traversal cost) of a partial solution.
int obj_function_parcial(const vector<const vector<int> *> solution) {
    int cost = 0;
    for (int r = 0; r < solution.size(); r++) {
        if(solution[r]->size() > 0){
            int sum = 0, cap = 0;
            cap = demanda[solution[r]->at(0)];
            sum = custo[solution[r]->at(0)];
            for (int i = 1; i < solution[r]->size(); i++) {
                sum += sp(solution[r]->at((unsigned long) (i - 1)), solution[r]->at((unsigned long) i), D);
                int taskid = solution[r]->at((unsigned long) i);
                //cout << taskid << "(" << nReqEdges << ")" << endl;
                cap += demanda[taskid];
                sum += custo[taskid];
            }
            if (cap > capacity) {
                printf("Error: Capacity exceed in the route (index = %d)\n", r);
                exit(1);
            }
            cost += sum;
        }
    }
    return cost;
}

// Calculates objective function (traversal cost) of a complete OCARP solution and verify its feasibility.
int objective_function(const vector<vector<int>> solution) {
    int cost = 0;
    set<int> conj;
    for (int r = 0; r < maxroutes; r++) {
        if(solution[r].size() > 0) {
            int sum = 0, cap = 0;
            cap = demanda[solution[r][0]];
            if (conj.count(solution[r][0]) > 0) {
                printf("Error: Route %d contains a repeated task! (task: %d)\n", r,
                           solution[r][0]);
                int *a = 0;
                *a = 0;
                exit(1);
            }

            conj.insert(solution[r][0]);
            ///printf("%d ", solution[r][0]);///

            for (int i = 1; i < solution[r].size(); i++) {
                sum += sp(solution[r][i - 1], solution[r][i], D);
                cap += demanda[solution[r][i]];
                // ASSERT
                //printf(" %d.%d, ", sum, cap);//
                if (conj.count(solution[r][i]) > 0) {
                    printf("Error: Route %d contains a repeated task! (task: %d)\n", r,
                           solution[r][i]);
                    int *a = 0;
                    *a = 0;
                    exit(1);
                }
                conj.insert(solution[r][i]);//
                //printf("%d ", solution[r][i]);//
            }

            /// ASSERT
            if (cap > capacity) {
                printf("Error: Capacity exceed in the route (index = %d)\n", r);
                exit(1);
            }


            //cout << "this route has cost = " << sum << endl;
            cost += sum;
        }
    }

    // ASSERT
    if (conj.size() != nReqEdges) {
        printf("Error: The solution does not contain all required edges.\n");
        exit(1);
    }

    for (int i = 1; i <= nReqEdges; i++) {
        if (conj.count(i) + conj.count(-i) < 1) {
            printf("Error: solution does not route the required edge (tasks %d/%d)\n", i, -i);
            exit(1);
        }
    }

    if (lb0_value <= 0) {
        printf("Trivial lower bound not computed or is zero. Please verify lb_0: %d\n", lb0_value);
        exit(1);
    }

    return cost + lb0_value;
}

// Calculates objective function (traversal cost) of a non-capacitated route.
int obj_function_naoCapacitada(const int solution[], const int solution_size) {
    int sum = 0;
    if(solution_size > 0){
        sum = custo[solution[0]];
        for (int i = 1; i < solution_size; i++) {
            sum += sp(solution[i - 1], solution[i], D);
            int taskid = solution[i];
            sum += custo[taskid];
        }
    }
    return sum;
}

// Continuous binary search function used by the SUS (Stochastic Universal Sampling) selection method.
// @arr[]: array containing the elements
// @ele: continuous value to be searched.
// Return: The index i such that @arr[i] <= @ele <= @arr[i+1]. In other words, the interval of @arr[] that contains the value of @ele. 
int binarySearchSpecial(const double arr[], double ele) {
    int first, last, middle;
    first = 0;
    last = POP - 1;
    middle = (first + last) / 2;

    while (first <= last) {
        if (ele >= arr[middle] && (middle >= (POP - 1) || ele <= arr[middle + 1])) {
            return middle;
        }
        else if ((middle <= 0 || ele >= arr[middle - 1]) && ele <= arr[middle]) {
            if (middle <= 0) return 0;
            else return middle - 1;
        }
        else if (arr[middle] < ele) {
            first = middle + 1;
        }
        else
            last = middle - 1;

        middle = (first + last) / 2;
    }
    if (first > last) {
        printf("Not found! %f is not present in the list.\n", ele);
        fflush(stdout);
        exit(1);
        return 1;
    }
    printf("*** ERROR: binarySearchSpecial. ");
    exit(1);
    return 1;
}

// Stochastic_universal_sampling by Baker.
void selectCrossover(vector<int> &parentChromosomes, const int quant) {
    if (quant % 2 != 0) {
        printf("***ERRO***: 'quant' Para crossover deve ser PAR!");
        exit(1);
    }
    double totalFitness = 0.0;
    double arrayFitnesses[POP + 1];
    for (int i = 0; i < POP; i++) {
        arrayFitnesses[i] = totalFitness;
        totalFitness += current_population->fitness[i];
        //cout << "sumndo " << current_population->fitness[i] << endl;
    }
//    PRINTF("Roulette values:\n");
//    for (int i=0; i < POP; i++){
//    PRINTF("%d - %f - %d\n", i, arrayFitnesses[i], current_population->obj_value[i]);
//    }
//    PRINTF("Total fitness: %f (%d solutions)\n\n", totalFitness, POP);

    // Universal Stochastic Selector
    double random = frandom() * totalFitness; // Random value
    double distPontos = totalFitness / POP;
    for (int i = 0; i < quant; ++i) {
        int willReproduce;
        // Get the individual that corresponds to the random value and then increase the random value to get the next individual
        willReproduce = binarySearchSpecial(arrayFitnesses, random);
        //PRINTF("Searching for %f we found the individual idx= %d.\n", random, willReproduce);
        parentChromosomes.push_back(willReproduce);
        if (random + distPontos < totalFitness)
            random = random + distPontos;
        else
            random = (random + distPontos) - totalFitness;
    }
}

// Crossover Operator C1 by Reeves.
void crossover(int pai1, int pai2, int offspring[GENE_SIZE]) {
    // A memory of tasks added to the solution.
    bool tasks_added[nTasks + 2];

    for (int i = 0; i <= nTasks; i++) {
        tasks_added[i] = false;
    }

    //PRINTF("\nMaking crossover of parents %d and %d.\n", pai1, pai2);
    //PRINTF("pai1: ");
    //for(int q = 0; q < nReqEdges; q++) PRINTF("%d ", current_population->individual[pai1].gene[q]);
    //PRINTF("\npai2: ");
    //for(int q = 0; q < nReqEdges; q++) PRINTF("%d ", current_population->individual[pai2].gene[q]);


    // Crossover operator C1 by Reeves
    int ponto1 = irandom(nReqEdges - 1);
    //PRINTF("irandom: %d\n", ponto1);
    for (int q = 0; q <= ponto1; q++) {
        offspring[q] = current_population->individual[pai1].gene[q];
        tasks_added[pos(offspring[q])] = true;
        tasks_added[pos(-offspring[q])] = true;
    }

    int q = ponto1 + 1;
    for (int i = 0; i < nReqEdges; i++) {
        if (!tasks_added[pos(current_population->individual[pai2].gene[i])]) {
            offspring[q] = current_population->individual[pai2].gene[i];
            q++;
        }
    }

    //PRINTF("child: ");
    //for(int q = 0; q < nReqEdges; q++) PRINTF("%d ", offspring[q]);
    //exit(1);
}

/*
  Population initialization:
    - Step 1: Non-capacitated route.
    - Step 2: Feasibilization procedure.
    - Step 3/4: Local search OCARP. / Chromosome remounting.
    How step1: Nearest neighbour greedy, then 2-opt.
    How step2: Split. If infeasible, select the best route regarding capacity, add to a new solution and solve the remaining tasks by step 1.
    How step3: (Inter-route) Deconstruction/Reconstruction local search, then (Intra-route) 2-opt for each route.
    How step4: Handles each route from the OCARP solution as a giant required arc. Find the best routing of these "giant arcs" by same methods of step 1. Then Split it. If costs were improved by that, back to step 3.
*/
void inicializar_populacao() {
    // Processamento da metaheurística
    vector<int> vectasks;
    int noncapacitated_route[nReqEdges];
    for (int i = 1; i <= nReqEdges; i++) {
        vectasks.push_back(i);
    }

    // Population initialization
    int pop_counter = 0;
    for (int q = 0; pop_counter < POP_SIZE; q++) {
	
        // Step 1: Non-capacitated route
        construcaoNaoCapacitada(vectasks, 0.00, noncapacitated_route);
        buscaLocal2opt(noncapacitated_route, (const int) vectasks.size());
		
		// Step 2: Feasibilization
        vector<vector<int> > solucao;
        bool factivel = factibilizar_dificil(noncapacitated_route, nReqEdges, maxroutes, solucao);
        if (factivel) {

            // Step 3: Local search (complete)
            int custoLS = local_search_OCARP(solucao);
            int verifyCost = objective_function(solucao);

            if( custoLS != verifyCost ) {
                cout << "Error custoLS != verifyCost: " << custoLS << "," << verifyCost << endl;
            }

            // Add individual to population
            current_population->individual[pop_counter].solucao = solucao;
            routes2noncapacitated_route(current_population->individual[pop_counter].gene, solucao);
            current_population->obj_value[pop_counter] = custoLS;
            numSolsFactiveis++;
            if ( custoLS < bestCost) {
                bestSolution = current_population->individual[pop_counter];
                bestCost = custoLS;
                //cout << "new bestCost found! bestCost = " << bestCost << endl;
                bestSolutionClock = clock();
                //writeSolution("bestSol.txt", bestSolution);
                // Checks if it's an optimal solution
                if( bestCost == lb0_value ){
                    return;
                }
            }
            current_population->fitness[pop_counter] = (CONST_FITNESS_DIV * (double) 1.0) / (custoLS - lb0_value);
            pop_counter++;
            
        }
        else{
            numSolsInfactiveis++;   
        }
    }
    POP = pop_counter;
}

// Local search OCARP
int local_search_OCARP(vector<vector<int> > &solucao){
	// OCARP complete local search
	int custoAfter;
	int custoLS;
	int custo1 = objective_function(solucao);
	
	do{
		// Step 1: inter-route
		solucao = clusterReconstruction(solucao, 4);
		// Step 2: intra-route
		intrarota2_opt(solucao);
		int custoLS = objective_function(solucao);
		
		// Step 3/4: Split-1 and then Split
		custoAfter = mergeEvaluate(solucao);

		if (custoAfter == -1 || custoLS < custoAfter) {
			cout << "Error: remounting procedure getting infeasible OR worst solution than the original solution. It actually should never happen." << endl;
			exit(1);
		}
	} while( custoAfter < custoLS ); // If chrosome remouting improves the solution, then a new local search and chromosome remounting is executed in a loop fashion.
	
	return custoAfter;
}

// Population restart.
void restart_populacao(){
    clock_t beginRestart = clock();
    //PRINTF("Restarting... ");
    vector<pair<int,int>> listaIndividuos;
    // Sort individuals by decreasing order of cost
    for(int i =0; i < POP; i++){
        listaIndividuos.push_back(pair<int,int>(current_population->obj_value[i], i));
    }
    std::sort(listaIndividuos.begin(), listaIndividuos.end(), std::greater<std::pair<int,int>>());
    // List of the eligible-to-be-replaced solutions (elitist selection)
    vector<int> listaCandidatosSubstituidos;
    for(int i = 0; i < POP - RESTART_POPULATION_BEST_PRESERVE; i++){
        listaCandidatosSubstituidos.push_back(listaIndividuos[i].second);
    }
    random_shuffle(listaCandidatosSubstituidos.begin(), listaCandidatosSubstituidos.end());
    // Choose at random the replaced solutions
    vector<int> listaSubstituidos;
    for(int i = 0; i < RESTART_POPULATION_NUM; i++){
        listaSubstituidos.push_back(listaCandidatosSubstituidos[i]);
    }
    vector<int> vectasks;
    for (int i = 1; i <= nReqEdges; i++) {
        vectasks.push_back(i);
    }
    // Create new individuals to replaced the selected old ones
    int k = 0;
    while(k < listaSubstituidos.size()){
        // Non-capacitated route
        int idx = listaSubstituidos[k];
        bool fac = false;
        while(!fac){
            fac = gerarNovoIndividuo(current_population->individual[idx].gene, current_population->individual[idx].solucao, vectasks);
            if(fac) numSolsFactiveis++;
            else numSolsInfactiveis++; 
        }
        if(fac){
            int custoGerada = objective_function(current_population->individual[idx].solucao);
            current_population->obj_value[idx] = custoGerada;
            if (custoGerada < bestCost) {
                bestSolution = current_population->individual[idx];
                bestSolutionClock = clock();
                bestCost = custoGerada;
                if (bestCost == lb0_value) return;
            }
            current_population->fitness[idx] = (CONST_FITNESS_DIV * (double) 1.0) / (custoGerada - lb0_value);
            k++;
            
        }
    }
    clock_t endRestart = clock();
    //PRINTF("restarting done in %f secs.\n", (double)(endRestart-beginRestart)/CLOCKS_PER_SEC);
    return;
}


bool gerarNovoIndividuo (int gene[GENE_SIZE], vector<vector<int>> &solutionOCARP, const vector<int> &vectasks) {
    solutionOCARP.clear();

    // Step 1: Non-capacitated route
    construcaoNaoCapacitada(vectasks, 0.00, gene);
    buscaLocal2opt(gene, (const int) vectasks.size());
	
	// Step 2: Feasibilization procedure
    bool factivel = factibilizar_dificil(gene, nReqEdges, maxroutes, solutionOCARP);

    if (factivel) {
		// Step 3: Local search routines
		local_search_OCARP(solutionOCARP);

        // Just transform the solution to a chromosome
		routes2noncapacitated_route(gene, solutionOCARP);
        return true;
    }
    else {
        return false;
    }
}

multimap<int, vector<int>, std::greater<int> > bestRoutesByCapacity;

// This algorithm uses the Split algorithm (Ulusoy) to achieve a feasible solution for OCARP.
// If the Split algorithm get an infeasible solution, then the best route regarding capacity usage is fixed to a new solution.
// Then the remaining required edges are solved as a smaller OCARP instance from zero using the same constructive methods of population initialization.
// @noncapacitated_route[]: non-capacitated route (chromosome)
// @solution_size: chromosome size
// @Kmax: # of vehicles
// @routesOCARP: solution (output)
// return: viability
bool factibilizar_dificil(const int noncapacitated_route[], const int solution_size, int Kmax,
                          vector<vector<int>> &routesOCARP) {
    int rotear[nReqEdges];
    set<int> conjDEBUG;
    routesOCARP.clear();

    // Copy the vector
    set<int> tasksToRoute;
    for (int i = 0; i < solution_size; i++) {
        rotear[i] = noncapacitated_route[i];
        tasksToRoute.insert(noncapacitated_route[i]);
    }

    int nRoteados = 0;
    for (int k = 0; k < Kmax; k++) {
        const int qtderoutes = Kmax - k;
        const int nTasks = solution_size - nRoteados;
        bool factivel;
        pair<int, int> routes_indexes[qtderoutes];
        factivel = factibilizacao_ulusoy(rotear, nTasks, qtderoutes, routes_indexes);

        if (factivel) {
            // Feasible solution success
            //cout << "Adicionando um total de " << qtderoutes << " routes na solucao para encerrar:" << endl;
            for (int i = 0; i < qtderoutes; i++) {
                vector<int> rota;
                //cout << "Rota " << i << ": ";
                if( routes_indexes[i].first != -1 && routes_indexes[i].second != -1 ){
                    for (int j = routes_indexes[i].first; j <= routes_indexes[i].second; j++) {
                        if (conjDEBUG.count(rotear[j]) > 0) {
                            cout << "Problema. Foi inserido um elemento repetido: " << rotear[j] << ". na rota " << k + i <<
                            ". size desta rota:" << (routes_indexes[i].first - routes_indexes[i].second + 1) << endl;
                            int *a = 0;
                            *a = 0;
                            exit(1);
                        }
                        rota.push_back(rotear[j]);
                        conjDEBUG.insert(rotear[j]);
                        conjDEBUG.insert(-rotear[j]);
                        //cout << rotear[j] << "(" << j << ") ";
                    }
                    routesOCARP.push_back(rota);
                    //cout  << endl;
                }
                else{
                    // Empty route -> required to avoid bugs
                    routesOCARP.push_back(rota);
                }
            }

            // Statistics
            recursoesFactivel[k]++;
            return true;
        }
        else {
            // We do not use restricted candidate list, just a greedy selection.
            double RCLcut, RCLmax = 0.0, RCLmin = BIG_INT_INFINITY;
            for (auto rota : bestRoutesByCapacity) {
                if (rota.first > RCLmax) {
                    RCLmax = rota.first;
                }
                if (rota.first < RCLmin){
                    RCLmin = rota.first;
                }
            }
            // RCL: all viable routes
            RCLcut = RCLmax - 0.1;
            // The code above is to be used only if one wants to implement RCL (restricted candidate list)
            vector<vector<int> *> RCLroutes;
            for (auto &rota : bestRoutesByCapacity) {
                if (rota.first >= RCLcut) {
                    RCLroutes.push_back(&(rota.second));
                }
            }
            // Select the best route regarding capacity usage
            int idxRand = irandom((int) (RCLroutes.size() - 1));
            vector<int> chosen = *RCLroutes.at(idxRand);
            int sumCap = 0;
            for(auto ele : chosen){
                sumCap += demanda[ele];
            }
            //printf("\nRota escolhida: Tasks de %d a %d (n.opcoes:%d). CAP usada = %d/%d, k = %d, Kmax=%d\n", *chosen.begin(), *chosen.rbegin(), RCLroutes.size(), sumCap, capacity, k, Kmax);

            // Check which tasks still need to be routed
            for (auto it = chosen.begin(); it != chosen.end(); it++) {
                conjDEBUG.insert(*it);
                conjDEBUG.insert(-*it);
                tasksToRoute.erase(*it);
                tasksToRoute.erase(-(*it));
            }

            // Remaining tasks vector (still need to be routed)
            int hue = 0;
            for (auto task : tasksToRoute) {
                rotear[hue] = task;
                hue++;
            }

            // Partial solution
            routesOCARP.push_back(chosen);

            // Number of tasks already routed
            nRoteados = nRoteados + chosen.size();

            // New constructive heuristic to make a non-capacitated route servicing only the remaining tasks
            if (true) {
                // Same method as population initialization
                vector<int> taskList;
                for (auto task: tasksToRoute) {
                    taskList.push_back(task);
                }
                construcaoNaoCapacitada(taskList, 0.01 * irandom(MAX_ALPHA_RCL), rotear);
                buscaLocal2opt(rotear, tasksToRoute.size());
            }
        }
    }

    // If after 'Kmax' iterations none viable solutions is obtained, then the individual is declared infeasible and discarded.
    return false;
}

// Split algorithm (by Ulusoy).
// It splits the non-capacitated route (chromosome) into M feasible routes. If it's not possible, then it returns the best routes regarding capacity usage at the global variable 'bestRoutesByCapacity'.
// @solution_naoCapacitada: non-capacitated route (chromosome).
// @routeSize: chromosome size
// @Kmax: # of vehicles available
// @routes_indexes: If feasible, this array contains the index intervals of noncapacitated_route[] that makes the M feasible routes. (output)
// \return true if feasible, false otherwise.
bool factibilizacao_ulusoy(const int noncapacitated_route[], int routeSize, int Kmax, pair<int, int> routes_indexes[]) {
    // Adds unitary sub-routes to 'bestRoutesByCapacity'
    {
        vector<int> trivial_route;
        bestRoutesByCapacity.clear();
        trivial_route.push_back(noncapacitated_route[0]);
        int thisCap = demanda[noncapacitated_route[0]];
        bestRoutesByCapacity.insert(pair<int, vector<int>>(thisCap, trivial_route));
    }

    // Step 1: Auxiliary graph creation

    // Vertexes creation
    vector<vector<int> > ulusoy_graph(routeSize + 1);
    for (int i = 0; i <= routeSize; i++)
        ulusoy_graph[i] = vector<int>();

    // Unitary sub-routes
    for (int i = 0; i < routeSize; i++)
        ulusoy_graph[i].push_back(0);

    // Non-unitary sub-routes (contains 2 or more required arcs).
    for (int i = 0; i < routeSize; i++) {
        int sum = 0;
        int cap = demanda[noncapacitated_route[i]];
        for (int j = i + 1; j < routeSize; j++) {
			// The cost of each arc is the deadheading traversal cost of that subroute.
            sum += sp(noncapacitated_route[j - 1], noncapacitated_route[j], D);
            cap += demanda[noncapacitated_route[j]];

			// Only feasible sub-routes regarding capacity constrains are considered
            if (cap <= capacity) {
                ulusoy_graph[i].push_back(sum);
                //printf("Rota não trivial adicionada: De sol[%d] ate sol[%d] (tasks %d a %d). Custo = %d, Cap = %d\n", i, j, noncapacitated_route[i], noncapacitated_route[j], sum, cap);
                
                vector<int> rota;
                for (int z = i; z <= j; z++) {
                    rota.push_back(noncapacitated_route[z]);
                }
                bestRoutesByCapacity.insert(pair<int, vector<int>>(cap, rota));
            }
            else {
                break;
            }
        }
    }

    // Step 2: Minimum path using at most 'Kmax' arcs in the graph
    int V[routeSize + 1], V2[routeSize + 1];
    vector<pair<int, int>> R[routeSize + 1];
    vector<pair<int, int>> R2[routeSize + 1];

    // Data initialization
    V[0] = V2[0] = 0;
    for (int i = 1; i <= routeSize; i++) {
        V[i] = V2[i] = BIG_INT_INFINITY;
    }

    // Bellman-Ford modified algorithm (minimum path with at most M arcs in a DAG)
    bool stable = false;
    for (int k = 0; k < Kmax && !stable; k++) {
        stable = true;
        for (int i = 0; i < routeSize; i++) {
            for (int j = 0; j < (int) ulusoy_graph[i].size(); j++) {
                int dest = i + j + 1;
                if (V[i] + ulusoy_graph[i][j] < V2[dest]) { // (R[i].size() > 0 || i == 0) &&
                    V2[dest] = V[i] + ulusoy_graph[i][j];
                    R2[dest] = R[i];
                    R2[dest].push_back(pair<int, int>(i, dest - 1));
                    stable = false;
                }
            }
        }
        for (int i = 1; i <= routeSize; i++) {
            V[i] = V2[i];
            R[i] = R2[i];
        }
    }

    // Verifica o caso onde não é possível encontrar uma solução factível com essa ordem de tasks (VAI acontecer nas instâncias mais difíceis)
    if (V[routeSize] >= BIG_INT_INFINITY) {
        //printf("Ulusoy: Nao foi possivel encontrar routes factiveis na solucao com o grafo de Ulusoy.\n");
        return false;
    }

    //printf("Ulusoy: Solution with cost %d\n", V[routeSize]);

    //printf("Solution indexes:\n");
    int k = 0;
    for (k = 0; k < (int) R[routeSize].size(); k++) {
        int first = R[routeSize][k].first, second = R[routeSize][k].second;
        routes_indexes[k].first = first;
        routes_indexes[k].second = second;
        //printf("(%d,%d);", first, second);
    }
    // In the case we have empty routes.
    // It can happens when the cost to route noncapacitated_route[] is zero.
    if( k < Kmax){
        //printf("Custo desta rota = %d", V[routeSize]);
        //printf("tivemos um caso de rota vazia. k=%d, kmax=%d\n", k, Kmax);
        //printf("Vou imprimir a primeira rota (apenas a 1a!):\n");
        for(int w = routes_indexes[0].first; w <= routes_indexes[0].second; w++){
            //printf("%d ", noncapacitated_route[w]);
        }
        //printf("\n");
        //exit(1);
    }
    while(k < Kmax){
        routes_indexes[k].first = -1;
        routes_indexes[k].second = -1;
        //printf("(vazio,vazio);\n");
        k++;
    }

    return true;
}

// Feasible routes -> Non-capacitated route
int routes2noncapacitated_route(int noncapacitated_route[], const vector<vector<int>> &routes) {
    int c = 0;
    for (auto rota : routes) {
        for (auto ele : rota) {
            noncapacitated_route[c++] = ele;
        }
    }
    return c;
}

// Non-capacitated route & feasible Split indexes -> Feasible routes
int noncapacitated_route2Routes(vector<vector<int>> &routes, const int noncapacitated_route[], const pair<int, int> routes_indexes[],
                      const int nRoutes) {
    routes.clear();
    int c = 0;
    for (int i = 0; i < nRoutes; i++) {
        vector<int> rota;
        if( routes_indexes[i].first != -1){
            for (int w = routes_indexes[i].first; w <= routes_indexes[i].second; w++) {
                rota.push_back(noncapacitated_route[w]);
                c++;
            }
        }
        else{
            // empty route
        }
        routes.push_back(rota);
    }
    return c;
}

// Remounting of the chromsome - Split-1
// This routine makes a new arrangement of the routes of the solution into a big non-capacitated route.
// Then it uses the Split algorithm to extract the best solution from that arrangement in the expectation to obtain an even better solution.
// \return Solution cost or -1 if infeasible.
int mergeEvaluate(vector<vector<int>> &routes) {
    int rotaGigante[nReqEdges];
    const int nTasks = mesclarroutes(rotaGigante, routes);
    const int nRoutes = routes.size();
    pair<int, int> routes_indexes[nRoutes];
    bool feas = factibilizacao_ulusoy(rotaGigante, nTasks, nRoutes, routes_indexes);
    if (feas) {
        noncapacitated_route2Routes(routes, rotaGigante, routes_indexes, nRoutes);
        return obj_function_parcial(routes);
    }
    else{
        cout << "*ERRO* It should never happens! Infeasible after routes rearrangement !!!" << endl;
        exit(1);
        return -1;
    }
}

// Print a named OCARP solution (DEBUG)
void printSolution(string name, const vector<vector<int>> &rota) {
    cout << "printSolution(" << name << "):" << endl;
    int i = 0;
    for (auto oneRoute : rota) {
        cout << "route_idx=" << i++ << ":" << endl;
        for (auto ele : oneRoute) {
            cout << ele << " ";
        }
        cout << endl;
    }
    cout << "*************************************************" << endl << endl;
}

// Inter-route local search
// Step 1: it identifies a list of the closest routes to a specific (i,j) \in E_R
// Step 2: it tries to reconstruct each pair of the closest routes into a new pair of routes. If the new routes have lower cost then they overwrite the previous routes in the solution.
// @rotaInicial: initial solution
// @sizeConjuntoR: parameter that limits the size of 'list of closest routes'.
// \return: the solution after local search.
vector<vector<int> > clusterReconstruction(const vector<vector<int>> &rotaInicial, int sizeConjuntoR) {
    vector<vector<int> > rotaInteira = rotaInicial;
    for (int t = 1; t <= nReqEdges; t++) {
        multimap<int, int> routesDistance;
        // Sort the routes by their distance to the required edge 't'
        for (int i = 0; i < rotaInteira.size(); i++) {
            int min = INT_MAX;
            if( rotaInteira[i].size() == 0){
                // empty route
                min = 0;
            }
            else{
                for (auto task : rotaInteira[i]) {
                    // Verify if this route contains 't'
                    if (task == t || task == -t) {
                        min = -1;
                        break;
                    }
                    if (sp(task, t, D) < min) // sp entre d-a
                        min = sp(task, t, D);
                    if (sp(task, -t, D) < min) // sp entre d-b
                        min = sp(task, -t, D);
                    if (sp(t, task, D) < min) // sp entre b-c
                        min = sp(t, task, D);
                    if (sp(-t, task, D) < min) // sp entre a-b
                        min = sp(-t, task, D);
                }
            }
			// pair<int,int> which .first is the distance and .second the index of the route
            routesDistance.insert(pair<int, int>(min, i));
        }
		
        // Select the 'sizeConjuntoR' closest routes.
        vector<int> routesConjuntoR;
        for (auto rotaPerto : routesDistance) {
            routesConjuntoR.push_back(rotaPerto.second);
            if (routesConjuntoR.size() == sizeConjuntoR) break;
        }
		
		// For each pair of the selected closest routes, do a reconstruction using same methods as population initialization.
        for (int w = 0; w < routesConjuntoR.size(); w++) {
            for (int k = w + 1; k < routesConjuntoR.size(); k++) {
                vector<vector<int> > sol;
                vector<int> conjuntoP;
                vector<const vector<int> *> routesPointers;
				
                // Data preparation
                const int p = routesConjuntoR[w], q = routesConjuntoR[k];
                for (auto task : rotaInteira[p]) {
                    conjuntoP.push_back(task);
                }
                for (auto task : rotaInteira[q]) {
                    conjuntoP.push_back(task);
                }
                routesPointers.push_back(&rotaInteira[p]);
                routesPointers.push_back(&rotaInteira[q]);
				
                if(conjuntoP.size() > 0){
                    bool feasible = clusterReconstruction_cluster(conjuntoP, 2, sol);
                    int costBefore = obj_function_parcial(routesPointers);
                    if (feasible) {
                        int costAfter = obj_function_parcial(sol);
                        if (costAfter < costBefore) {
							// Solutions are replaced only when it lowers the cost.
                            rotaInteira[p] = sol[0];
                            rotaInteira[q] = sol[1];
                        }
                    }
                }
            }
        }
    }
    return rotaInteira;
}

// Reconstruction procedure
// \return true when feasible, false otherwise.
bool clusterReconstruction_cluster(const vector<int> &taskCluster, const int nroutes, vector<vector<int>> &solCluster) {
    int noncapacitated_route[nReqEdges];
    construcaoNaoCapacitada(taskCluster, 0.0, noncapacitated_route, D);
    buscaLocal2opt(noncapacitated_route, taskCluster.size());
    return factibilizar_dificil(noncapacitated_route, taskCluster.size(), nroutes, solCluster);
}

// Intra-route local search
// The 2-opt local search.
// \return optimized solution
vector<vector<int> > intrarota2_opt(const vector<vector<int>> &rotaInicial) {
    vector<vector<int> > novaRota = rotaInicial;
    for (int i = 0; i < rotaInicial.size(); i++) {
        int *array = &novaRota[i][0];
        buscaLocal2opt(array, novaRota[i].size(), D);
    }
    return novaRota;
}


// R[][] is a matrix of shortest paths that are used in the chromosome rearrangement procedure.
// They represent the shortest paths between routes of a solution on graph I(V,E \cup E_S).
int **R;

// From a OCARP solution, it creates a non-capacitated chromosome with low deadheading cost between routes.
// It works by using the same greedy constructive method from non-capacitated route, but now we simulate 'virtual required arcs' (x,y) for each route such that x is the starting vertex of the first required arc and y' the ending vertex of the last required arc.
// Then we route these 'virtual required arcs' into a non-capacitated route. Thus getting a rearrangement of the routes into a non-capacitated route with optimized deadheading cost.
// @noncapacitated_route: optimized chromosome (output)
// @routes: OCARP solution (input)
// \return Number of routes
int mesclarroutes(int noncapacitated_route[], const vector<vector<int>> &routes) {
	// Each route can be considered a "giant required arc".
	// These tasks are (x,y) for each route such that x is the starting vertex of the first required arc and y' the ending vertex of the last required arc.
	// For each required arc we have two tasks: (x,y) and (y,x).

    // 0. Find the starting and ending vertexes of each route
    vector<pair<int, int> > extremos(routes.size());
    set<int> emptyRoutes; // empty routes
    for (int i = 0; i < routes.size(); i++) {
        if(routes[i].size() == 0){
            emptyRoutes.insert(i);
        }
        else{
            extremos[i].first = getNodes(routes[i].at(0)).first;
            extremos[i].second = getNodes(*(routes[i].rbegin())).second;
        }
    }

	// 1. Fills matrix R (shortest path distances between 'tasks-routes')
    for (int i = 1; i <= routes.size(); i++) {
        if(emptyRoutes.count(i-1)) continue;
        pair<int, int> nodes_i(extremos[i - 1].first, extremos[i - 1].second); //(u,v) that represents route i
        for (int j = 1; j <= routes.size(); j++) {
            if(emptyRoutes.count(j-1)) continue;
            pair<int, int> nodes_j(extremos[j - 1].first, extremos[j - 1].second); //(u,v) that represents route j

            if (i == j) {
                R[pos(i)][pos(j)] = INT_MAX;
                R[pos(i)][pos(-j)] = INT_MAX;
                R[pos(-i)][pos(j)] = INT_MAX;
                R[pos(-i)][pos(-j)] = INT_MAX;
            }
            else {
                // The 4 possibilities (tasks inverted or not)
                R[pos(i)][pos(j)] = spG[nodes_i.second][nodes_j.first];
                R[pos(i)][pos(-j)] = spG[nodes_i.second][nodes_j.second];
                R[pos(-i)][pos(j)] = spG[nodes_i.first][nodes_j.first];
                R[pos(-i)][pos(-j)] = spG[nodes_i.first][nodes_j.second];
            }
        }
    }

    // 2. Checks if matrix R[][] makes sense
    for (int i = 1; i <= routes.size(); i++) {
        if(emptyRoutes.count(i-1)) continue;
        for (int j = 1; j <= routes.size(); j++) {
            if(emptyRoutes.count(j-1)) continue;
            if (i != j) {
                if (R[pos(i)][pos(j)] !=
                    spG[getNodes(*(routes[i - 1].rbegin())).second][getNodes(routes[j - 1].at(0)).first])
                    printf("Problem on matrix R[][]! 1\n");
                if (R[pos(-i)][pos(j)] != spG[getNodes(routes[i - 1].at(0)).first][getNodes(routes[j - 1].at(0)).first])
                    printf("Problem on matrix R[][]! 2\n");
            }
        }
    }

    // Non-capacitated solution
    vector<int> listaRouteTasks;
    for (int i = 1; i <= routes.size(); i++) {
        if(emptyRoutes.count(i-1)) continue;
        listaRouteTasks.push_back(i);
    }

    int routesOrder[listaRouteTasks.size()];
    //cout << "Chamando a construcaoNaoCapacitada(): (total de " << listaRouteTasks.size() << " routes-tarefas)." << endl;
    construcaoNaoCapacitada(listaRouteTasks, 0.0, routesOrder, R);
    //cout << "Chamando a rotina 2-opt: (total de " << listaRouteTasks.size() << " routes-tarefas)." << endl;
    buscaLocal2opt(routesOrder, listaRouteTasks.size(), R);
    //cout << "2opt finalizado." << endl;

    // Makes a non-capaciated chromosome from the 'tasks-route' codification we were using until now.
    int lastTask = -1, sumInterroutes = 0;
    int k = 0;
    for (int i = 0; i < listaRouteTasks.size(); i++) {
        int rotaIdx = routesOrder[i];
        if (rotaIdx > 0) {
            const vector<int> &rota = routes[rotaIdx - 1];
            for (auto ele : rota) {
                noncapacitated_route[k++] = ele; // normal task
            }
            // estatistica
            if (lastTask != -1) {
                sumInterroutes += sp(lastTask, *rota.begin(), D);
            }
            lastTask = *rota.rbegin();
        }
        else {
            const vector<int> &rota = routes[-rotaIdx - 1];
            for (auto it = rota.rbegin(); it != rota.rend(); it++) {
                noncapacitated_route[k++] = -(*it); // inverted task (because the entire route is inversed)
            }
            // estatistica
            if (lastTask != -1) {
                sumInterroutes += sp(lastTask, -*rota.rbegin(), D);
            }
            lastTask = -(*rota.begin());
        }
    }

    return k;
}

// Constructs a non-capacitated solution.
// Uses the greedy nearest neighbour heuristic.
// @vecTasks: Tasks to be routed
// @alfa: RCP parameter *not used in this heuristic*
// @outputSolution: Non-capacitated route (output)
// @matriz: distance matrix (can be D[][] or R[][]).
void construcaoNaoCapacitada(const vector<int> &vecTasks, double alfa, int outputSolution[], int **matriz) {
    bool visitados[nTasks + 1];

    if( alfa > 0.0 ){
        cout << "Error: alpha greater than zero. But this heuristic does not uses RCL. Alpha: " << alfa << endl;
        exit(1);
    }

    for (int i = 1; i <= nTasks; i++) {
        visitados[i] = false;
    }

    int rand_idx = irandom(vecTasks.size() - 1);
    int taskInicial = vecTasks[rand_idx];
    int x1 = taskInicial, x2 = taskInicial, y;
    int tasksAdicionadas = 0;
    list<int> outputList;

    //printf("Initializing route with task=%d (idx=%d)\n", taskInicial, rand_idx);
    outputList.push_back(taskInicial);
    tasksAdicionadas++;
    visitados[pos(taskInicial)] = true;
    visitados[pos(-taskInicial)] = true;

    // Select nearest neighbour until all tasks inserted
    while (tasksAdicionadas < vecTasks.size()) {
        int menor = INT_MAX;
        int maior = INT_MIN;
        vector<int> conjuntoCandidatos;
        vector<int> conjuntoRCL;

        // Feasible tasks (tasks still not included in the solution)
        for (int k = 0; k < (int) vecTasks.size(); k++) {
            int t = vecTasks[k];
			// Let x1 be the task at the END of the route, x2 be the task at the START of the route.
            if (!visitados[pos(t)] && !visitados[pos(-t)]) {
                // Considers task t and its inversion.
                conjuntoCandidatos.push_back(t);
                conjuntoCandidatos.push_back(-t);

                // 1) Considers the insertion at the end of the route
                if (sp(x1, t, matriz) < menor)
                    menor = sp(x1, t, matriz);
                if (sp(x1, t, matriz) > maior)
                    maior = sp(x1, t, matriz);
                // Inversed task
                if (sp(x1, -t, matriz) < menor)
                    menor = sp(x1, -t, matriz);
                if (sp(x1, -t, matriz) > maior)
                    maior = sp(x1, -t, matriz);
                // 1) Considers the insertion at the start of the route
                if (sp(t, x2, matriz) < menor)
                    menor = sp(t, x2, matriz);
                if (sp(t, x2, matriz) > maior)
                    maior = sp(t, x2, matriz);
                // Inversed task
                if (sp(-t, x2, matriz) < menor)
                    menor = sp(-t, x2, matriz);
                if (sp(-t, x2, matriz) > maior)
                    maior = sp(-t, x2, matriz);
            }
        }

        // Restricted candidate list (disabled for OCARP)
        double limiteRCL = menor + alfa * (maior - menor);
        for (int i = 0; i < (int) conjuntoCandidatos.size(); i++) {
            if (sp(x1, conjuntoCandidatos[i], matriz) <= limiteRCL ||
                sp(conjuntoCandidatos[i], x2, matriz) <= limiteRCL) {
                conjuntoRCL.push_back(conjuntoCandidatos[i]);
            }
        }

        // Random element from RCL
        y = irandom(conjuntoRCL.size() - 1);
        y = conjuntoRCL[y];
        if (sp(x1, y, matriz) < sp(y, x2, matriz)) {
            outputList.push_back(y);
//            printf("Inseri %d na rota (custo %d)\n\n", y, sp(x1,y,matriz));
            x1 = y;
        }
        else {
            outputList.push_front(y);
//            printf("Inseri %d na rota (custo %d)\n\n", y, sp(y,x2,matriz));
            x2 = y;
        }
        tasksAdicionadas++;
        visitados[pos(y)] = true;
        visitados[pos(-y)] = true;
    }

    // Verification
    if (tasksAdicionadas != (int) vecTasks.size()) {
        printf("ERRO: Solucao construida com erro. %d != %d\n", tasksAdicionadas, (int) vecTasks.size());
        exit(1);
    }

    // From list to vector
    int i = 0;
    for (auto it = outputList.begin(); it != outputList.end(); it++) {
        outputSolution[i++] = *it;
    }

    //printf("### Finalizando Heuristica Nearest Neighbour ###\n");
    return;
}

// Busca local 2-OPT integrada com a vizinhança de reversão de um arco
// Resolve o 2-OPT para uma rota não-capacitada.
// EDIT1: Acho que preciso remover essa ideia de reversão de arco.
void buscaLocal2opt(int currentSolution[], const int solution_size, int **matriz) {
    // Check cost before 2-opt
    int avaliaAntes = 0;
    if (matriz == D) {
        avaliaAntes = obj_function_naoCapacitada(currentSolution, solution_size);
    }

    // 2-OPT until local minimum
    if (solution_size <= 2) return; // not possible
    bool REPETIR_2OPT = true;
    while (REPETIR_2OPT) {
        REPETIR_2OPT = false;
        //map<int, pair<int,int>> goodMoves;
        for (int i = 0; i < solution_size; i++) {
            // The code above inverts the direction of a single arc
//            if (solution_size >= 2) {
//                int x = i;
//                int diff;
//
//                if (x == solution_size - 1) {
//                    diff = (sp(currentSolution[x - 1], -currentSolution[x], matriz)) -
//                           (sp(currentSolution[x - 1], currentSolution[x], matriz));
//                }
//                else if (x == 0) {
//                    diff = (sp(-currentSolution[x], currentSolution[x + 1], matriz)) -
//                           (sp(currentSolution[x], currentSolution[x + 1], matriz));
//                }
//                else {
//                    diff = (sp(currentSolution[x - 1], -currentSolution[x], matriz) +
//                            sp(-currentSolution[x], currentSolution[x + 1], matriz)) -
//                           (sp(currentSolution[x - 1], currentSolution[x], matriz) +
//                            sp(currentSolution[x], currentSolution[x + 1], matriz));
//                }
//
//                if (diff < 0) {
//                    REPETIR_2OPT = true;
//                    //if(IMPROVEMENT_BEST) {
//                    //    goodMoves.insert(pair<int, pair<int,int>>(diff, pair<int,int>(x, x)));
//                    //}
//                    //else{
//                        currentSolution[x] = -currentSolution[x];
//                    //}
//                }
//            }


            // 2-OPT neighbourhood
            for (int j = i + 1; j < solution_size; j++) {
                int x = i;
                int y = j;

                // *** 2-OPT neighbourhood ***
                // Removes two edges, adds other two. The two removed edges makes an interval. The tasks within the interval are inversed.
                // Removes two edges: [x-1] to [x] (except if x==0); and [y] to [y+1] (except if y==solution_size);
                // Add other two: [x-1] to [y] (except if x==0); and [x] to [y+1] (except if y==solution_size);

                if (x == 0 && y == solution_size - 1) continue;
                int diff = 0;

				if( y < solution_size - 1 && x > 0){
					diff =  (sp(currentSolution[x - 1], -currentSolution[y], matriz) +
							sp(-currentSolution[x], currentSolution[y + 1], matriz)) -
							(sp(currentSolution[x - 1], currentSolution[x], matriz) +
							sp(currentSolution[y], currentSolution[y + 1], matriz));
				}

                if (diff < 0) {
                    REPETIR_2OPT = true;
                    //if(IMPROVEMENT_BEST) {
                    //    goodMoves.insert(pair<int, pair<int,int>>(diff, pair<int,int>(x, y)));
                    //}
                    //else{
					while (x <= y) {
						int aux = -currentSolution[x];
						currentSolution[x] = -currentSolution[y];
						currentSolution[y] = aux;
						x++;
						y--;
					}
                    //}
                }
            }
        }

        // Makes only the best 2-opt movement available (best-improvement)
//        if(IMPROVEMENT_BEST && goodMoves.size() > 0) {
//            int x = (*goodMoves.begin()).second.first;
//            int y = (*goodMoves.begin()).second.second;
//            while (x <= y) {
//                int aux = -currentSolution[x];
//                currentSolution[x] = -currentSolution[y];
//                currentSolution[y] = aux;
//                x++;
//                y--;
//            }
//        }
    }

    // checks cost after
    if (matriz == D) {
        int avaliaDepois = obj_function_naoCapacitada(currentSolution, solution_size);
        if (avaliaDepois > avaliaAntes) {
            cout << "2-opt increasing cost!!! Before= " <<
            avaliaAntes << " After= " << avaliaDepois << endl;
            exit(1);
        }
    }
    return;
}

// Write a solution into a file.
void writeSolution (char* filename, const Solution &sol){
    FILE* file;
    file = fopen(filename, "w");
    if(file == NULL){
        cout << "It was not possible to create the output-file " << filename << endl;
        cout << "Please consider to create the directory manually and check write permissions." << endl;
        exit(1);
    }
    fprintf(file, "-------------------\nINSTANCE ATTRIBUTES\n-------------------\n");
    fprintf(file,"NAME: %s\n", strname);
    fprintf(file,"VEHICLES: %d\n", maxroutes);
    fprintf(file,"CAPACITY: %d\n", capacity);
    fprintf(file,"NODES: %d\n", nNodes);
    fprintf(file,"EDGES: %d\n", nEdges);
    fprintf(file,"REQUIRED_EDGES: %d\n", nReqEdges);
    fprintf(file,"<NODE1> <NODE2> <REQ> <COST> <DEMAND>\n");
    for (ListGraph::EdgeIt e(*g); e!=INVALID; ++e){
        fprintf(file,"%d %d %d %.2f %.2f\n", g->id(g->u(e))+1, g->id(g->v(e))+1, ((*demandaAresta)[e]>0?1:0), (double) (*custoAresta)[e], (double) (*demandaAresta)[e]);
    }
    fprintf(file,"\n\n\n");
    fprintf(file, "-------------------\nSOLUTION ATTRIBUTES\n-------------------\n");
    fprintf(file, "PATH_REQUIRED_ARCS <no.> <cost> <remaining capacity> <# req. arcs>: <reqArc 1-start>-<reqArc 1-end> <reqArc 2-start>-<reqArc 2-end> ... <reqArc k-start>-<reqArc k-end>\n");
    double sumCostAllRoutes = 0.0;
    for(int i = 0; i < sol.solucao.size(); i++){
        double sumCost = 0.0; double sumCapacity = 0.0;
        for(int j = 0; j < sol.solucao[i].size(); j++){
            sumCapacity += demanda[sol.solucao[i].at(j)];
            sumCost += custo[sol.solucao[i].at(j)];
            if( j+1 < sol.solucao[i].size() ){
                sumCost += sp(sol.solucao[i].at(j), sol.solucao[i].at(j+1), D);
            }
        }
        sumCostAllRoutes += sumCost;
        fprintf(file, "PATH %d %.1f %.1f %d: ", i+1, sumCost, (double) capacity-sumCapacity, (int) sol.solucao[i].size());
        for(int j = 0; j < sol.solucao[i].size(); j++){
            if( sol.solucao[i].at(j) >= 0 )
                fprintf(file, "%d-%d ", g->id(g->u(edgeFromTask[sol.solucao[i].at(j)]))+1, g->id(g->v(edgeFromTask[sol.solucao[i].at(j)]))+1);
            else
                fprintf(file, "%d-%d ", g->id(g->v(edgeFromTask[sol.solucao[i].at(j)]))+1, g->id(g->u(edgeFromTask[sol.solucao[i].at(j)]))+1);
        }
        fprintf(file, "\n");
    }
    fprintf(file, "(Note: subsequent required arcs are traversed through their shortest paths)\n");
    fprintf(file, "\nTOTAL_COST = %.1f\n\n", sumCostAllRoutes);
    fclose(file);
}

// This function encapsulates the complexity to access matrix D (or R).
// Obs: tasks original directions are [1,nReqEdges] and its inversed directions are [-1,-nReqEdges].
inline int pos(int task) {
    if (task > 0)
        return task;
    else
        return nReqEdges + (-task);
}

// This function encapsulates the complexity to access matrix D (or R).
// Gets the shortest path between two tasks (from 'p' to 'q', note that its different from 'q' to 'p')
inline int sp(int p, int q, int **T) {
    return T[pos(p)][pos(q)];
}

// Get node ids from a task.
inline pair<int, int> getNodes(int task) {
    ListGraph::Edge e = edgeFromTask.at(task);
    if (task > 0) {
        return pair<int, int>((*g).id((*g).u(e)), (*g).id((*g).v(e))); // (u,v)
    }
    else {
        return pair<int, int>((*g).id((*g).v(e)), (*g).id((*g).u(e))); // (v,u)
    }
    // Note that these indexes are from the LEMON indexing, they are not the indexes used in the graph from the instance file.
}

// Preprocessing of the algorithm.
// Calculates the shortest path matrix between required arcs (tasks).
void pre_processamento() {
    // Allocates the matrix
    nTasks = nReqEdges * 2;
    D = new int *[nTasks + 1];
    R = new int *[nTasks + 1];
    for (int i = 1; i <= nTasks; i++) {
        D[i] = new int[nTasks + 1];
        R[i] = new int[nTasks + 1];
    }

    // Checking
    for(int i = 1; i <= nReqEdges; i++){
        //ListGraph::Edge e = edgeFromTask.at(i);
        //cout << "task " << i << " : " << getNodes(i).first << ", " << getNodes(i).second << endl;
        //cout << "task " << -i << " : " << getNodes(-i).first << ", " << getNodes(-i).second << endl;
    }

    // Fills the matrix

    // 1. All Pairs Shortest Path of G
    spG = vector<vector<int> >(nNodes); // sp[x][y]: shortest path from x to y (obs: sp[x][y] == sp[y][x]).
    for (int i = 0; i < nNodes; i++)
        spG[i] = vector<int>(nNodes);

    // 2. Compute shortest path from node s to each node
    for (ListGraph::NodeIt n1(*g); n1 != INVALID; ++n1) {
        //cout << endl << "Analisando distancias de " << g.id(n1) << ":" << endl;
        ListGraph::NodeMap<int> dists(*g);
        dijkstra((*g), (*custoAresta) ).distMap(dists).run(n1);

        for (ListGraph::NodeIt n2(*g); n2 != INVALID; ++n2) {
            //cout << "Para " << g.id(n2) << " = " << dists[n2] << ", ";
            spG[(*g).id(n1)][(*g).id(n2)] = dists[n2];
        }
    }

	// 2. To each pair of tasks (inversed or not), calculates the correspondent entries of distances between them
    for (int i = 1; i <= nReqEdges; i++) {
        pair<int, int> nodes_i = getNodes(i);
        for (int j = 1; j <= nReqEdges; j++) {
            pair<int, int> nodes_j = getNodes(j);

            if (i == j) {
                D[pos(i)][pos(j)] = INT_MAX;
                D[pos(i)][pos(-j)] = INT_MAX;
                D[pos(-i)][pos(j)] = INT_MAX;
                D[pos(-i)][pos(-j)] = INT_MAX;
            }
            else {
                // The 4 possibilities: each task inversed or not
                D[pos(i)][pos(j)] = spG[nodes_i.second][nodes_j.first];
                D[pos(i)][pos(-j)] = spG[nodes_i.second][nodes_j.second];
                D[pos(-i)][pos(j)] = spG[nodes_i.first][nodes_j.first];
                D[pos(-i)][pos(-j)] = spG[nodes_i.first][nodes_j.second];
            }
        }
    }

    // Checks the matrix D validity
    for (int i = 1; i <= nReqEdges; i++) {
        for (int j = 1; j <= nReqEdges; j++) {
            if (i != j) {
                if (D[pos(i)][pos(j)] != spG[getNodes(i).second][getNodes(j).first])
                    PRINTF("PROBLEM on matrix! 1\n");
                if (D[pos(-i)][pos(j)] != spG[getNodes(-i).second][getNodes(j).first])
                    PRINTF("PROBLEM on matrix! 2\n");
                if (D[pos(i)][pos(-j)] != spG[getNodes(i).second][getNodes(-j).first])
                    PRINTF("PROBLEM on matrix! 3\n");
                if (D[pos(-i)][pos(-j)] != spG[getNodes(-i).second][getNodes(-j).first])
                    PRINTF("PROBLEM on matrix! 4\n");
            }
        }
    }
    //printf("### Fim pre-processamento. ###\n\n");
}

// Read the instance file and initialize data used by the HGA.
void readFile(const string filepath, ListGraph &g, ListGraph::EdgeMap<int> &custoAresta, ListGraph::EdgeMap<int> &demandaAresta) {
    std::ifstream infile(filepath); // -std=c++11
    std::string line;
    nNodes = nTasks = nEdges = nReqEdges = maxroutes = capacity = 0;
    if( infile.is_open() == false ){
        cout << "File could not be opened: " << filepath << endl;
        exit(1);
    }
    int sumCustoRequeridas = 0;
    while (getline(infile, line)) {
        //cout << "Line reading: " << line << endl;
        char ch;
        ch = line.at(0);
        switch (ch) {
            case 'p':
				// Initial instance data
                sscanf(line.c_str(), "%*s %*s %d %d %d %d", &nNodes, &nEdges, &maxroutes, &capacity);
                maxroutes += M_plus;
                for (int i = 0; i < nNodes; i++) {
                    g.addNode();
                }
                nReqEdges = 0;
                break;
            case 'e': {
				// Edge reading
                int u, v, c, d;
                ListGraph::Edge edg;
                sscanf(line.c_str(), "%*s %d %d %d %d", &u, &v, &c, &d); // edge (u,v), cost c, demand d.
                edg = g.addEdge(g.nodeFromId(u - 1), g.nodeFromId(v - 1));
                custoAresta[edg] = c;
                demandaAresta[edg] = d;
                if (d > 0){
                    sumCustoRequeridas += c;
                    nReqEdges++;
                    edgeFromTask.insert(pair<int, ListGraph::Edge>(nReqEdges, edg));
                    edgeFromTask.insert(pair<int, ListGraph::Edge>(-nReqEdges, edg));
                    custo.insert(pair<int, int>(nReqEdges, c));
                    custo.insert(pair<int, int>(-nReqEdges, c));
                    demanda.insert(pair<int, int>(nReqEdges, d));
                    demanda.insert(pair<int, int>(-nReqEdges, d));
                }
            }
                break;
            default:
                cout << "Instance reading problem: character unknown:" << ch << endl;
                exit(1);
                break;
        }
    }
	
	// Trivial lower bound: sum of cost of required edges
    lb0_value = sumCustoRequeridas;

    // Asserts
    int nnos = 0, narestas = 0;
    for (ListGraph::NodeIt n(g); n != INVALID; ++n)
        nnos++;
    for (ListGraph::EdgeIt e(g); e != INVALID; ++e)
        narestas++;
    if (nnos != nNodes || narestas != nEdges) {
        cout << "Problema com leitura de nos ou arestas. (" << nnos << "!=" << nNodes << ") ou (" << narestas << "!=" <<
        nEdges << ")" << endl;
        exit(1);
    }
	return;
}
