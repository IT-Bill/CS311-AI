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

#ifndef OCARP_GA_MAIN_H
#define OCARP_GA_MAIN_H

#include <iostream>
#include <sstream>
#include <fstream>
#include <climits>
#include <cstring>
#include <ctime>
#include <set>
#include <functional>
#include <algorithm>
#include <lemon/list_graph.h>
#include <lemon/euler.h>
#include <lemon/dijkstra.h>

using namespace lemon;
using namespace std;

// ================================================== CONSTANTS AND PARAMETERS ============================================================


// The "DEBUG" flag turns ON debug printfs
#define DEBUG

#ifdef DEBUG
#define PRINTF(...) printf(__VA_ARGS__)
#else
#define PRINTF(...)
#endif

#define BIG_INT_INFINITY INT_MAX/2

// Static sizes
#define GENE_SIZE 200
#define POP_SIZE 20
#define STATISTICAL_FILTER_SAMPLE_SIZE 100

// Genetic Algorithm - other parameters
#define CONST_FITNESS_DIV 100
#define RESTART_POPULATION_BEST_PRESERVE 1
#define RESTART_POPULATION_NUM 10
extern double LOCALSEARCH_FILTER_MULTIPLIER;
extern int RESTART_INTERVAL;

#define MAX_ALPHA_RCL 0

extern int POP;

// ================================================== DATA STRUCTS ============================================================

// HGA solution (or individual)
typedef struct solution {
    int gene[GENE_SIZE];
    vector< vector<int> > solucao;
} Solution;

// HGA Population
typedef struct population {
    Solution individual[ POP_SIZE];
    int obj_value[ POP_SIZE];
    double fitness[ POP_SIZE];
    multimap<int, int > ordered;
} Population;

// ================================================== GLOBAL VARIABLES ============================================================

// Instance data
extern int nTasks;
extern int nNodes, nEdges;
extern int nReqEdges;
extern int maxroutes;
extern int capacity;

// Graph data
extern ListGraph *g;
extern ListGraph::EdgeMap<int> *custoAresta;
extern ListGraph::EdgeMap<int> *demandaAresta;

// Preprocessed/Computed graph data
extern vector< vector<int> > spG; // Shortest path on G
extern int **D;
extern map<int, ListGraph::Edge> edgeFromTask;
extern map<int, int> custo;
extern map<int, int> demanda;
extern int lb0_value;

// HGA population
extern Population pop1, pop2;
extern Population* current_population;
extern Population* other_population;

// Stochastic filter from local search
extern vector<int> filterSampleBefore;
extern vector<int> filterSampleAfter;
extern double filterMean;
extern double filterStdDeviation;

// Best solution (output)
extern Solution bestSolution;
extern int bestCost;

// Execution parameters
extern int LIMITE_TEMPO;
extern int M_plus;

// Statistics
extern int recursoesFactivel[];

// ================================================== METHODS AND FUNCTIONS ============================================================

// Preprocessing
void pre_processamento();
inline int pos (int task);
inline int sp (int p, int q, int **T); // To access shortest path between tasks
inline pair<int,int> getNodes (int task); // To access nodes from tasks
inline pair<int,int> getNodes (ListGraph::Edge e);

// HGA main components
void genetic_algorithm();
void inicializar_populacao();
void selectCrossover (vector<int> &selectedChromosomes, const int quant);
int  binarySearchSpecial (const double arr[], double ele);
void crossover (int pai1, int pai2, int offspring[GENE_SIZE]);
//void mutation (int candidate[], const int solution_size);
void restart_populacao();

// Auxiliary functions
int objective_function(const vector<vector<int>> solucao );
int obj_function_parcial(const vector<vector<int>> solucao );
int obj_function_parcial(const vector<const vector<int>*> solucao );

// Non-capacitated Routes
int obj_function_naoCapacitada(const int solution[], const int solution_size );
void construcaoNaoCapacitada(const vector<int>& vecTasks, double alfa, int outputSolution[], int **matriz = D);
void buscaLocal2opt(int currentSolution[], const int solution_size, int **matriz = D);

// Factiblization
bool gerarNovoIndividuo (int gene[GENE_SIZE], vector<vector<int>> &solutionOCARP, const vector<int> &vectasks);
bool factibilizar_dificil (const int solucaoNaoCapacitada[], const int solution_size, int Kmax, vector<vector<int>> &routesOCARP);
bool factibilizacao_ulusoy (const int solution_naoCapacitada[], int nRotear, int Kmax, pair<int,int> particionamento[]);

// Chromosome remounting (routes rearrangement)
int mesclarroutes (int noncapacitated_route[], const vector<vector<int>> &routes);
int mergeEvaluate (vector<vector<int>> &routes);

// Conversion between route representations
int routes2noncapacitated_route (int noncapacitated_route[], const vector<vector<int>> &routes);
int noncapacitated_route2Routes (vector<vector<int>> &routes, const int noncapacitated_route[], const pair<int,int> particionamento[], const int nroutes);

// Local search
int local_search_OCARP(vector<vector<int> > &solucao);
vector< vector<int> > clusterReconstruction (const vector<vector<int>> &rotaInicial, int sizeConjuntoR);
bool clusterReconstruction_cluster (const vector<int> &taskCluster, const int nroutes, vector<vector<int>> &solCluster);
vector< vector<int> > intrarota2_opt (const vector<vector<int>> &rotaInicial);

// Reading functions
void readFile(const string filePath, ListGraph &g, ListGraph::EdgeMap<int> &custo, ListGraph::EdgeMap<int> &demanda);

// Output functions
void writeSolution (char* filename, const Solution &sol);

// Random number generators
double frandom(); // Real \in [0, 1]
int irandom(int a); // Integer \in [0, a]

#endif //OCARP_GA_MAIN_H
