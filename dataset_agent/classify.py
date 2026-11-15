from __future__ import annotations

from .models import NormalizedDataset


DOMAIN_TERMS = {
    "oncology": {"cancer", "tumor", "oncology", "carcinoma"},
    "cardiovascular": {"heart", "cardiac", "cardiovascular", "hypertension"},
    "neurology": {"brain", "neuro", "alzheimer", "parkinson"},
    "infectious_disease": {"virus", "viral", "infection", "covid", "influenza"},
}

OMICS_TERMS = {
    "genomics": {"genome", "genomic", "dna", "variant", "vcf"},
    "transcriptomics": {"transcriptome", "rna-seq", "gene expression", "single-cell rna"},
    "proteomics": {"proteome", "proteomic", "protein", "mass spectrometry"},
    "epigenomics": {"epigenome", "methylation", "chip-seq", "atac-seq"},
}


def enrich_classification(dataset: NormalizedDataset) -> NormalizedDataset:
    text = " ".join([dataset.title, dataset.description, *dataset.raw_metadata.get("keywords", [])]).lower()
    if dataset.domain == "unknown":
        for domain, terms in DOMAIN_TERMS.items():
            if any(term in text for term in terms):
                dataset.domain = domain
                break
    if not dataset.omics_layer:
        dataset.omics_layer = sorted(
            layer for layer, terms in OMICS_TERMS.items() if any(term in text for term in terms)
        )
    if dataset.domain == "unknown":
        dataset.information_gaps.append("Domain could not be classified from available metadata")
    if not dataset.omics_layer:
        dataset.information_gaps.append("Omics layer could not be classified from available metadata")
    return dataset

