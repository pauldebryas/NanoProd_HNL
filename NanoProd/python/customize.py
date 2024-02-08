import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import Var
from RecoTauTag.RecoTau.tauIdWPsDefs import WORKING_POINTS_v2p5

def customizeGenParticles(process):
  def pdgOR(pdgs):
    abs_pdgs = [ f'abs(pdgId) == {pdg}' for pdg in pdgs ]
    return '( ' + ' || '.join(abs_pdgs) + ' )'

  leptons = pdgOR([ 11, 13, 15 ])
  important_particles = pdgOR([ 6, 23, 24, 25, 35, 39, 9990012, 9900012, 1000015 ])
  process.finalGenParticles.select = [
    'drop *',
    'keep++ statusFlags().isLastCopy() && ' + leptons,
    '+keep statusFlags().isFirstCopy() && ' + leptons,
    'keep+ statusFlags().isLastCopy() && ' + important_particles,
    '+keep statusFlags().isFirstCopy() && ' + important_particles,
    "drop abs(pdgId) == 2212 && abs(pz) > 1000", #drop LHC protons accidentally added by previous keeps
  ]

  for coord in [ 'x', 'y', 'z']:
    setattr(process.genParticleTable.variables, 'v'+ coord,
            Var(f'vertex().{coord}', float, precision=10,
                doc=f'{coord} coordinate of the gen particle production vertex'))

  return process

def customizeTaus(process):
  deepTauCuts = []
  for deep_tau_ver in [ "2017v2p1", "2018v2p5" ]:
    cuts = []
    e_VVVLoose = WORKING_POINTS_v2p5["e"]["VVVLoose"]
    mu_VLoose = WORKING_POINTS_v2p5["mu"]["VLoose"]
    jet_VVVLoose = WORKING_POINTS_v2p5["jet"]["VVVLoose"]
    for vs, wp, score in [ ("e", "VVVLoose", e_VVVLoose), ("mu", "VLoose", mu_VLoose), ("jet", "VVVLoose", jet_VVVLoose) ]:
      if deep_tau_ver == "2018v2p5":
        cuts.append(f"tauID('byDeepTau{deep_tau_ver}VS{vs}raw') > {score}")
      else:
        cuts.append(f"tauID('by{wp}DeepTau{deep_tau_ver}VS{vs}')")
    cut = "(" + " && ".join(cuts) + ")"
    deepTauCuts.append(cut)
  deepTauCut = "(tauID('decayModeFindingNewDMs') > 0.5 && (" + " || ".join(deepTauCuts) + "))"
  pnetCut = "( isTauIDAvailable('byPNetVSjetraw') && tauID('byPNetVSjetraw') > 0.05 )"

  process.finalTaus.cut = f"pt > 18 && ( {deepTauCut} || {pnetCut} )"
  return process

def FixHNL2016HIPM(process):
  process.lowPtElectronTask = cms.Task()
  process.lowPtElectronTablesTask = cms.Task()
  process.lowPtElectronMCTask = cms.Task()
  process.boostedTauTask = cms.Task()
  process.boostedTauTablesTask = cms.Task()
  process.boostedTauMCTask = cms.Task()
  process.linkedObjects.lowPtElectrons = "finalElectrons"
  process.linkedObjects.boostedTaus = "finalTaus"
  del process.jetTable.variables.hfadjacentEtaStripsSize
  del process.jetTable.variables.hfcentralEtaStripSize
  del process.jetTable.variables.hfsigmaEtaEta
  del process.jetTable.variables.hfsigmaPhiPhi
  return process

def customize(process):
  isHNL2016HIPM = True

  process.MessageLogger.cerr.FwkReport.reportEvery = 100
  process = customizeGenParticles(process)
  process = customizeTaus(process)
  if isHNL2016HIPM:
    process = FixHNL2016HIPM(process)

  return process
