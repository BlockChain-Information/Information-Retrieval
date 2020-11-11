import torch
import matplotlib.pyplot as plt
import numpy as np
import argparse
import pickle
import os
from torchvision import transforms
from build_vocab import Vocabulary
from model import EncoderCNN, DecoderRNN
from PIL import Image


class Class_Torch:
    # Device configuration
    # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def __init__(self):
        print('Class_Torch..__init__')
        #device = torch.device('cpu')
        return

    def load_image(self, image_path, transform=None):
        image = Image.open(image_path).convert('RGB')
        image = image.resize([224, 224], Image.LANCZOS)

        if transform is not None:
            image = transform(image).unsqueeze(0)

        return image

    # def predict(args):
    def predict(self, args):
        print('predict..start')
        device = torch.device('cpu')

        self.embed_size = 256
        self.hidden_size = 512
        self.num_layers = 1
        self.encoder_path = 'models/encoder-10-3000.ckpt'
        self.decoder_path = 'models/decoder-10-3000.ckpt'
        self.vocab_path = './data/vocab.pkl'
        self.image_path = 'png/example.png'
        self.device = torch.device('cpu')

        # Image preprocessing
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406),
                                 (0.229, 0.224, 0.225))])

        print('Load vocabulary wrapper...=', self.vocab_path)
        # Load vocabulary wrapper
        # Load vocabulary wrapper
        vocab = Vocabulary()

        print('Load vocabulary wrapper...=', self.vocab_path)

        with open(args.vocab_path, 'rb') as f:
            vocab = pickle.load(f)

        # Build models
        encoder = EncoderCNN(args.embed_size).eval()  # eval mode (batchnorm uses moving mean/variance)
        decoder = DecoderRNN(args.embed_size, args.hidden_size, len(vocab), args.num_layers)
        encoder = encoder.to(device)
        decoder = decoder.to(device)

        # Load the trained model parameters
        encoder.load_state_dict(torch.load(args.encoder_path, map_location=device))
        decoder.load_state_dict(torch.load(args.decoder_path, map_location=device))

        # Prepare an image
        image = self.load_image(args.image, transform)
        image_tensor = image.to(device)

        # Generate an caption from the image
        feature = encoder(image_tensor)
        sampled_ids = decoder.sample(feature)
        sampled_ids = sampled_ids[0].cpu().numpy()  # (1, max_seq_length) -> (max_seq_length)

        # Convert word_ids to words
        sampled_caption = []
        for word_id in sampled_ids:
            word = vocab.idx2word[word_id]
            sampled_caption.append(word)
            if word == '<end>':
                break
        sentence = ' '.join(sampled_caption)

        # Print out the image and the generated caption
        print(sentence)
        return sentence


def main(args):
    lib_torch = Class_Torch()
    lib_torch.predict(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str, default='png/example.png', help='input image for generating caption')
    parser.add_argument('--encoder_path', type=str, default='models/encoder-10-3000.ckpt',
                        help='path for trained encoder')
    parser.add_argument('--decoder_path', type=str, default='models/decoder-10-3000.ckpt',
                        help='path for trained decoder')
    parser.add_argument('--vocab_path', type=str, default='data/vocab.pkl', help='path for vocabulary wrapper')

    # Model parameters (should be same as paramters in train.py)
    parser.add_argument('--embed_size', type=int, default=256, help='dimension of word embedding vectors')
    parser.add_argument('--hidden_size', type=int, default=512, help='dimension of lstm hidden states')
    parser.add_argument('--num_layers', type=int, default=1, help='number of layers in lstm')
    args = parser.parse_args()
    main(args)