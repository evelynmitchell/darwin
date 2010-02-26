# -*- coding: utf-8 -*-

import math
import sys

from scipy import stats
import pylab

from darwin.robomendel import *
from darwin.entropy import *
import darwin.mixture


def plot_im_ip_bernoulli():
    n = 100
    simulation_model = stats.bernoulli(0.25)
    outcomes = simulation_model.rvs(n)

    ## log of uninformitive prior
    prior = stats.bernoulli(0.5)
    lup = discrete_sample_Le(outcomes, prior)

    steps = 100
    im_points = []
    ip_points = []
    sum_points = []
    for i in range(1, steps):
        ## likelihood of observations from model
        mean = float(i) / steps
        model = stats.bernoulli(mean)
        l_e = discrete_sample_Le(outcomes, model)
        i_m = l_e - lup
        im_points.append((mean, i_m.mean))

        h_e = box_entropy(outcomes, 7)
        i_p = -l_e - h_e
        ip_points.append((mean, i_p.mean))
        
        print mean, i_m.mean, i_p.mean

        sum_points.append((mean, i_p.mean + i_m.mean))

    pylab.plot([x for (x,y) in im_points], [y for (x,y) in im_points])
    pylab.plot([x for (x,y) in ip_points], [y for (x,y) in ip_points])
    pylab.plot([x for (x,y) in sum_points], [y for (x,y) in sum_points])
    pylab.xlabel('success of bernoulli')
    pylab.ylabel('Im (blue), Ip (green), Im + Ip (red)')
    pylab.grid(True)
    pylab.show()


def plot_im_ip_normal():
    n = 8
    simulation_model = stats.norm(10, 1)
    outcomes = simulation_model.rvs(n)

    ## log of uninformitive prior
    prior = stats.uniform(0, 20)
    lup = sample_Le(outcomes, prior)

    steps = 100
    im_points = []
    ip_points = []
    sum_points = []
    for i in range(100):
        ## likelihood of observations from model
        mean = 8. + 4. * i / steps
        model = stats.norm(mean, 1)
        l_e = sample_Le(outcomes, model)
        i_m = l_e - lup
        im_points.append((mean, i_m.mean))

        h_e = box_entropy(outcomes, 7)
        i_p = -l_e - h_e
        ip_points.append((mean, i_p.mean))

        sum_points.append((mean, i_p.mean + i_m.mean))

    pylab.plot([x for (x,y) in im_points], [y for (x,y) in im_points])
    pylab.plot([x for (x,y) in ip_points], [y for (x,y) in ip_points])
    pylab.plot([x for (x,y) in sum_points], [y for (x,y) in sum_points])
    pylab.xlabel('mean of normal')
    pylab.ylabel('Im, Ip')
    pylab.grid(True)
    pylab.show()

def plot_im_asym_normal():
    im_points = []
    simulation_model = stats.norm(0, 1)

    m = 300
    n = 300

    obs_list = list(simulation_model.rvs(n))
    sample = simulation_model.rvs(m)

    for i in range(3, n):
        obs = numpy.core.array(obs_list[0:i])
        mean = numpy.average(obs)
        var = numpy.average(obs * obs) - mean * mean
        model_obs = stats.norm(mean, math.sqrt(var))
        l_e = box_entropy(obs, min(len(obs)-1, 7), sample=sample)
        log_prior = sample_Le(sample, model_obs)
        i_m = -l_e - log_prior
        im_points.append((i, i_m.mean))

    pylab.plot([x for (x,y) in im_points], [y for (x,y) in im_points])
    pylab.xlabel('sample_size')
    pylab.ylabel('Im')
    pylab.grid(True)
    pylab.show()


def plot_im_asym_bernoulli():
    im_points = []
    simulation_model = stats.bernoulli(0.25)

    m = 300
    n = 100

    obs_list = list(simulation_model.rvs(n))
    sample = simulation_model.rvs(m)

    for i in range(3, n):
        obs = obs_list[0:i]
        count = obs.count(1)
        p = float(count) / i
        model_obs = stats.bernoulli(p)
        
        l_e = box_entropy(obs, min(len(obs)-1, 7), sample=sample)
        log_prior = discrete_sample_Le(sample, model_obs)
        i_m = -l_e - log_prior
        im_points.append((i, i_m.mean))
        print p, i_m.mean


    pylab.plot([x for (x,y) in im_points], [y for (x,y) in im_points])
    pylab.xlabel('sample_size')
    pylab.ylabel('Im')
    pylab.grid(True)
    pylab.show()

def compute_ip_discrete(outcomes, model):
    h_e = He_discrete(outcomes)
    l_e = discrete_sample_Le(outcomes, model)
    i_p = -h_e - l_e
    return i_p

def compute_ip_continuous(outcomes, model):
    h_e = box_entropy(outcomes, 7)
    l_e = sample_Le(outcomes, model)
    i_p = -h_e - l_e
    return i_p

def compute_im_discrete(outcomes, model, prior):
    l_e = discrete_sample_Le(outcomes, model)
    log_prior = LogPVector(prior)
    i_m = l_e - log_prior
    return i_m

def compute_im_continuous(outcomes, model, prior):
    l_e = sample_Le(outcomes, model)
    #log_prior = LogPVector(prior)
    log_prior = sample_Le(outcomes, prior)
    i_m = l_e - log_prior
    return i_m

def progeny_model(d, cross=None):
    if cross == 'Pu':
        return Multinomial({'y': 1-d, 'n': d})
    if cross == 'Wh':
        return Multinomial({'y': 1, 'n': 0})
    return None

def color_model(e, w):
    modelPu = stats.norm(10, 1)
    modelWh = stats.norm(0, 1)
    modelMix = darwin.mixture.Mixture(((1-e*w, modelPu), (e*w, modelWh)))
    return modelMix

def robomendel_wh_pu_crosses(n, d, e, w, outcomes, cross='Wh'):
    """Cross: 'Wh' for Wh x Wh, 'Pu' for Wh x Pu"""

    # Progeny experiment, compute im ip ie
    prior = numpy.array([math.log(0.5)]*n)
    model = progeny_model(d, cross)

    offspring_obs = []
    for off in outcomes:
        if off is not None:
            offspring_obs.append('y')
        else:
            offspring_obs.append('n')

    i_m = compute_im_discrete(offspring_obs, model, prior)
    i_p = compute_ip_discrete(offspring_obs, model)

    print "  Progeny observation"
    print "  Im: %s, Ip: %s" % (i_m.mean, i_p.mean)

    offspring = [x for x in outcomes if x is not None]
    if len(offspring) != n:
        print "%s offspring are dead" % (n - len(offspring),)

    if not offspring:
        print "  All progeny dead, no color observations"
        return

    color_obs = [p.rvs()[0] for p in offspring]
    # Color experiment, compute im ip ie
    # prior is uniform over color detector range
    model = color_model(e, w)
    prior = stats.uniform(-10, 30) # [-10, 20]
    i_m = compute_im_continuous(color_obs, model, prior)
    i_p = compute_ip_continuous(color_obs, model)

    print "  Color observation"
    print "  Im: %s, Ip: %s" % (i_m.mean, i_p.mean)


def main():
    """ Experimental parameters
    n == sample size
    d == probability that Wh is a different species
    e == probability that white color is an environmental effect
    w == probability of white flowers from environmental effect """

    n = 50
    (d, e, w) = (0.8, 0.2, 0.1)
    print "Experiment parameters"
    print "d: %s, e: %s, w: %s" % (d,e,w)
    print ""

    white_plant = PeaPlant(genome=PeaPlant.white_genome)
    purple_plant = PeaPlant(genome=PeaPlant.purple_genome)

    test_outcomes = [ [None]*n, [white_plant]*n, [purple_plant]*n ]
    offspring = [purple_plant]*(int((1-w)*n))
    offspring.extend([white_plant]*(int(w*n)))
    test_outcomes.append(offspring)

    #offspring = [white_plant * purple_plant for i in range(n)]

    for outcomes in test_outcomes:
        print "Test Outcomes", multiset(outcomes)
        print "Wh x Wh"
        robomendel_wh_pu_crosses(n, d, e, w, outcomes, cross='Wh')
        print "Wh x Pu"
        robomendel_wh_pu_crosses(n, d, e, w, outcomes, cross='Pu')
        print ""

if __name__ == '__main__':
    sys,exit(main())


