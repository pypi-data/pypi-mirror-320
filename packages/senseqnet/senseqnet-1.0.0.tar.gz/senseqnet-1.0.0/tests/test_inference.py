# run_senseqnet.py

from senseqnet.inference import predict_senescence

# Specify your input FASTA file
fasta_file = "./senseqnet/data/negative_0.4.fasta"  # Replace with your actual FASTA file path

# Predict senescence using the pretrained model in senseqnet.pth
results = predict_senescence(fasta_path=fasta_file, device="cpu")

# Print the results
print("\nPrediction Results:")
for result in results:
    print(
        f"SeqID: {result['sequence_id']} | "
        f"Label: {result['prediction_label']} | "
        f"Prob[Negative]: {result['probability_negative']:.4f} | "
        f"Prob[Positive]: {result['probability_positive']:.4f}"
    )
