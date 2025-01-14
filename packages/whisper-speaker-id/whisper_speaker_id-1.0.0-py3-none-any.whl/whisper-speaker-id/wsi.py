import torch
import torchaudio
import torch.nn.functional as F
from transformers import AutoFeatureExtractor, WhisperModel
from torch.nn import Module, Sequential, Linear, ReLU
from scipy.spatial.distance import cosine

AUDIO_SAMPLING_RATE = 16000
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class EncoderOnlyEmbeddingExtractor(Module):
    """
    Encoder-only model for embedding extraction.
    """
    def __init__(self, whisper_model, embed_dim):
        super().__init__()
        self.encoder = whisper_model.encoder  
        self.projection = Sequential(
            Linear(whisper_model.config.d_model, embed_dim),
            ReLU(),
            Linear(embed_dim, embed_dim)
        )

    def forward(self, input_features):
        encoder_states = self.encoder(input_features).last_hidden_state  
        pooled = encoder_states.mean(dim=1)
        embeddings = self.projection(pooled)
        return embeddings


def load_model(model_path, embed_dim=256, model_id="openai/whisper-tiny"):
    """
    Load the encoder-only model and feature extractor.
    
    Args:
        model_path (str): Path to the saved encoder-only model.
        embed_dim (int): Dimension of the embedding.
        model_id (str): Whisper model ID from Hugging Face.

    Returns:
        model (Module): Loaded encoder-only model.
        feature_extractor (AutoFeatureExtractor): Feature extractor for audio preprocessing.
    """
    whisper_model = WhisperModel.from_pretrained(model_id).to(DEVICE)
    model = EncoderOnlyEmbeddingExtractor(whisper_model, embed_dim).to(DEVICE)
    state_dict = torch.load(model_path, map_location=DEVICE)
    model.load_state_dict(state_dict['model_state_dict'])
    model.eval()
    feature_extractor = AutoFeatureExtractor.from_pretrained(model_id)
    return model, feature_extractor


def load_audio(audio_path):
    """
    Load and resample an audio file.
    
    Args:
        audio_path (str): Path to the audio file.

    Returns:
        numpy.ndarray: Resampled audio waveform.
    """
    waveform, sr = torchaudio.load(audio_path)
    if sr != AUDIO_SAMPLING_RATE:
        resampler = torchaudio.transforms.Resample(sr, AUDIO_SAMPLING_RATE)
        waveform = resampler(waveform)
    return waveform.squeeze(0).numpy()


def get_embedding(model, feature_extractor, audio_path):
    """
    Generate an embedding for a given audio file.
    
    Args:
        model (Module): Encoder-only model for embedding extraction.
        feature_extractor (AutoFeatureExtractor): Feature extractor for preprocessing audio.
        audio_path (str): Path to the audio file.

    Returns:
        numpy.ndarray: Generated embedding.
    """
    audio_array = load_audio(audio_path)
    with torch.no_grad():
        input_features = feature_extractor(
            audio_array, sampling_rate=AUDIO_SAMPLING_RATE, return_tensors="pt"
        ).input_features.to(DEVICE)
        embedding = model(input_features).squeeze(0).cpu().numpy()
    return embedding


def calculate_similarity(embedding1, embedding2):
    """
    Calculate the similarity score between two embeddings.
    
    Args:
        embedding1 (numpy.ndarray): First embedding.
        embedding2 (numpy.ndarray): Second embedding.

    Returns:
        float: Cosine similarity score (1 - cosine distance).
    """
    return 1 - cosine(embedding1, embedding2)


def process_single_audio(model, feature_extractor, audio_path):
    """
    Generate an embedding for a single audio file.
    
    Args:
        model (Module): Encoder-only model for embedding extraction.
        feature_extractor (AutoFeatureExtractor): Feature extractor for preprocessing audio.
        audio_path (str): Path to the audio file.

    Returns:
        numpy.ndarray: Generated embedding.
    """
    return get_embedding(model, feature_extractor, audio_path)


def process_audio_pair(model, feature_extractor, audio_path1, audio_path2):
    """
    Generate embeddings for two audio files and calculate their similarity.
    
    Args:
        model (Module): Encoder-only model for embedding extraction.
        feature_extractor (AutoFeatureExtractor): Feature extractor for preprocessing audio.
        audio_path1 (str): Path to the first audio file.
        audio_path2 (str): Path to the second audio file.

    Returns:
        float: Similarity score between the two audio files.
    """
    embedding1 = get_embedding(model, feature_extractor, audio_path1)
    embedding2 = get_embedding(model, feature_extractor, audio_path2)
    return calculate_similarity(embedding1, embedding2)
