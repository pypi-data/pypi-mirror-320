# TODO Responsabilidade: Carregar JSON de dataset (Label Studio) e treinar modelo de detecção de keypoints (salvar modelo pasta ml_models/keypoint_detection)
# TODO Pensar se salva também no Kaggle (ou se é melhor fazer isso manualmente)

# import json
# import os

# import cv2
# import keras
# import numpy as np
# from keras import layers
# from cucaracha.ml_training.ml_pattern import MLPattern


# class KeypointDetectionModeling(MLPattern):
#     def __init__(self, dataset_path: str, model_path: str):
#         super().__init__(dataset_path, model_path)
#         self.dataset = self.load_dataset()
#         self.model = None   # TODO If already exist a ML model, load it here
#         self.img_size = 224
#         self.num_keypoints = 4

#         self.loss = 'mse'
#         self.optmizer = keras.optimizers.Adam(1e-4)

#     def load_dataset(self, dataset_path: str = None):
#         super().load_dataset()
#         raw_data_folder = os.path.join(self.dataset_path, 'raw_data')
#         label_studio_json = os.path.join(
#             self.dataset_path, 'label_studio_export.json'
#         )
#         with open(label_studio_json, 'r') as f:
#             dataset = json.load(f)

#         train_dataset = []
#         for img_item in os.listdir(raw_data_folder):
#             for json_item in dataset:
#                 filename = json_item['data']['img']
#                 if img_item in filename.split(os.sep)[-1]:
#                     aux = {}
#                     aux['img_filename'] = img_item
#                     aux['annotations'] = json_item['annotations'][0]['result']
#                     train_dataset.append(aux)

#         return train_dataset

#     def get_model(self):
#         # Load the pre-trained weights of MobileNetV2 and freeze the weights
#         backbone = keras.applications.MobileNetV2(
#             weights=None,
#             include_top=False,
#             input_shape=(self.img_size, self.img_size, 3),
#         )
#         # backbone.trainable = False
#         backbone.trainable = True

#         inputs = layers.Input((self.img_size, self.img_size, 3))
#         x = keras.applications.mobilenet_v2.preprocess_input(inputs)
#         x = backbone(x)
#         x = layers.Dropout(0.3)(x)
#         x = layers.SeparableConv2D(
#             self.num_keypoints, kernel_size=5, strides=1, activation='relu'
#         )(x)
#         outputs = layers.SeparableConv2D(
#             self.num_keypoints, kernel_size=3, strides=1, activation='sigmoid'
#         )(x)

#         return keras.Model(inputs, outputs, name='keypoint_detector')

#     def create_augmented_datasets(self, batch_size=32, validation_split=0.2):
#         datagen = tf.keras.preprocessing.image.ImageDataGenerator(
#             rescale=1.0 / 255,
#             rotation_range=20,
#             width_shift_range=0.2,
#             height_shift_range=0.2,
#             shear_range=0.2,
#             zoom_range=0.2,
#             horizontal_flip=True,
#             fill_mode='nearest',
#             validation_split=validation_split,
#         )

#         train_generator = KeypointDataGenerator(
#             self.dataset,
#             self.dataset_path,
#             datagen,
#             batch_size=batch_size,
#             subset='training',
#         )

#         validation_generator = KeypointDataGenerator(
#             self.dataset,
#             self.dataset_path,
#             datagen,
#             batch_size=batch_size,
#             subset='validation',
#         )

#         return train_generator, validation_generator

#     def train_model(self):
#         model = self.get_model()
#         model.compile(loss=self.loss, optimizer=self.optmizer)
#         model.fit(
#             train_dataset, validation_data=validation_dataset, epochs=EPOCHS
#         )
#         # TODO Implementar treinamento do modelo de detecção de keypoints
#         # TODO Salvar modelo treinado na pasta ml_models/keypoint_detection
#         # TODO Salvar modelo treinado no Kaggle
#         return None

#     def __str__(self):
#         return self.get_model().summary()


# class KeypointDataGenerator(keras.utils.Sequence):
#     def __init__(
#         self,
#         dataset,
#         dataset_path,
#         datagen,
#         batch_size=32,
#         img_size=224,
#         num_keypoints=4,
#         subset='training',
#     ):
#         self.dataset = dataset
#         self.dataset_path = dataset_path
#         self.datagen = datagen
#         self.batch_size = batch_size
#         self.img_size = img_size
#         self.num_keypoints = num_keypoints
#         self.subset = subset
#         self.indexes = np.arange(len(self.dataset))
#         self.on_epoch_end()

#     def __len__(self):
#         return int(np.floor(len(self.dataset) / self.batch_size))

#     def __getitem__(self, index):
#         indexes = self.indexes[
#             index * self.batch_size : (index + 1) * self.batch_size
#         ]
#         batch_samples = [self.dataset[k] for k in indexes]

#         images, keypoints = self.__data_generation(batch_samples)
#         return images, keypoints

#     def on_epoch_end(self):
#         np.random.shuffle(self.indexes)

#     def __data_generation(self, batch_samples):
#         images = np.empty((self.batch_size, self.img_size, self.img_size, 3))
#         keypoints = np.empty(
#             (self.batch_size, self.img_size, self.img_size, self.num_keypoints)
#         )

#         for i, sample in enumerate(batch_samples):
#             img_path = os.path.join(
#                 self.dataset_path, 'raw_data', sample['img_filename']
#             )
#             image = cv2.imread(img_path)
#             image = cv2.resize(image, (self.img_size, self.img_size))
#             image = image / 255.0

#             keypoint = np.zeros(
#                 (self.img_size, self.img_size, self.num_keypoints)
#             )
#             for kp in sample['annotations']:
#                 x = int(kp['value']['x'] * self.img_size / 100)
#                 y = int(kp['value']['y'] * self.img_size / 100)
#                 keypoint[y, x, :] = 1

#             augmented = self.datagen.random_transform(
#                 image=image, keypoints=keypoint
#             )
#             images[i] = augmented['image']
#             keypoints[i] = augmented['keypoints']

#         return images, keypoints
