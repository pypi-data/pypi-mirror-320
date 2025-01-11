from __future__ import division
from TINTOlib.abstractImageMethod import AbstractImageMethod
import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math
from typing import Union

class SuperTML(AbstractImageMethod):
    default_pixels = 224
    default_font_size = 10
    default_feature_importance = False  # False to produce SuperTML-EF, True to produce SuperTML-VF
    default_random_seed = 1
    
    def __init__(
        self,
        problem = None,
        verbose = None,
        pixels=default_pixels,
        font_size = default_font_size,
        feature_importance: bool = default_feature_importance,
        random_seed: int = default_random_seed
    ):
        super().__init__(problem=problem, verbose=verbose)

        self.image_pixels: int = pixels
        self.font_size: int = font_size
        self.feature_importance: bool = feature_importance
        self.random_seed = random_seed

    def __saveSupervised(self, y, i, image):
        extension = 'png'  # eps o pdf
        subfolder = str(int(y)).zfill(2)  # subfolder for grouping the results of each class
        name_image = str(i).zfill(6)
        route = os.path.join(self.folder, subfolder)
        route_complete = os.path.join(route, name_image + '.' + extension)
        # Subfolder check
        if not os.path.isdir(route):
            try:
                os.makedirs(route)
            except:
                print("Error: Could not create subfolder")

        image.save(route_complete)
        route_relative = os.path.join(subfolder, name_image+ '.' + extension)
        return route_relative
    
    def __saveRegressionOrUnsupervised(self, i, image):
        extension = 'png'  # eps o pdf
        subfolder = "images"
        name_image = str(i).zfill(6) + '.' + extension
        route = os.path.join(self.folder, subfolder)
        route_complete = os.path.join(route, name_image)
        if not os.path.isdir(route):
            try:
                os.makedirs(route)
            except:
                print("Error: Could not create subfolder")
        image.save(route_complete)

        route_relative = os.path.join(subfolder, name_image)
        return route_relative
    
    # def calculate_feature_importance(self, data):
    #     # Dummy implementation, replace with actual feature importance calculation
    #     # Example: {'feature_0': 0.1, 'feature_1': 0.4, 'feature_2': 0.5}
    #     return {f'feature_{i}': np.random.rand() for i in range(data.shape[1])}

    def check_overlap(self, x, y, text_width, text_height, positions):
        for px, py, pw, ph in positions:
            if not (x + text_width < px or x > px + pw or y + text_height < py or y > py + ph):
                return True
        return False

    def __event2img(self,event: np.ndarray):
        # SuperTML-VF
        if self.feature_importance:
            padding = 5     # Padding around the texts

            feature_importances = self.feature_importances
            max_feature_importances = max(feature_importances.tolist())

            img = Image.fromarray(np.zeros([self.image_pixels, self.image_pixels, 3]), 'RGB')
            draw = ImageDraw.Draw(img)

            sorted_features = sorted(zip(event, feature_importances), key=lambda x: x[1], reverse=True)
            positions = []

            for i,(feature,importance) in enumerate(sorted_features):
                # The font size of this feature is relative to the ratio of this importante vs the most important feature
                ratio = (importance / max_feature_importances)
                font_size = max(int(self.font_size * ratio), 1)
                font = ImageFont.truetype("arial.ttf", font_size)

                text = f'{feature:.3f}'

                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                placed = False
                for y in range(0, self.image_pixels - text_height, 1):
                    if placed:
                        break
                    for x in range(0, self.image_pixels - text_width, 1):
                        if not self.check_overlap(x, y, text_width, text_height, positions):
                            positions.append((x, y, text_width+padding, text_height+padding))
                            draw.text((x, y), text, fill=(255, 255, 255), font=font)
                            placed = True
                            break

            return img

        # SuperTML-EF
        else:
            cell_width = self.image_pixels // self.columns
            rows = math.ceil(len(event) / self.columns)
            cell_height = self.image_pixels // rows

            font = ImageFont.truetype("arial.ttf", self.font_size)
            img = Image.fromarray(np.zeros([self.image_pixels, self.image_pixels, 3]), 'RGB')
            draw = ImageDraw.Draw(img)

            for i, f in enumerate(event):
                x = ((i % self.columns)) * cell_width
                y = (i // self.columns) * cell_height

                text = f'{f:.3f}'
                
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                text_x = x + (cell_width - text_width) / 2
                text_y = y + (cell_height - text_height) / 2

                draw.text(
                    (text_x, text_y),
                    text,
                    fill=(255, 255, 255),
                    font=font,
                )

            return img
        
    def calculate_feature_importances(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Calculates feature importances using a Random Forest model.

        Arguments
        ---------
        X: np.ndarray
            Feature array
        y: np.ndarray
            Targets array
        """
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

        max_selection = 100_000

        indices = np.arange(X.shape[0])
        np.random.shuffle(indices)

        # Split the data into training and testing sets
        if self.problem == 'supervised':
            model = RandomForestClassifier(random_state=self.random_seed, n_jobs=-1)
        else:
            model = RandomForestRegressor(random_state=self.random_seed, n_jobs=-1)

        # Fit the model
        model.fit(X[indices][:max_selection], y[indices][:max_selection])

        # Update the feature importances
        self.feature_importances = model.feature_importances_
        
    
    def _trainingAlg(self, x: pd.DataFrame, y: Union[pd.DataFrame, None]):
        X = x.values
        Y = y.values if y is not None else None

        # Variable for regression problem
        imagesRoutesArr = []

        if self.feature_importance:
            # Calculate the feature importance for SuperTML-VF
            self.calculate_feature_importances(X, Y)
        else:
            # Calculate the number of columns
            self.columns = math.ceil(math.sqrt(X.shape[1]))

        try:
            os.makedirs(self.folder)
            if self.verbose:
                print("The folder was created " + self.folder + "...")
        except:
            if self.verbose:
                print("The folder " + self.folder + " is already created...")
        for i in range(X.shape[0]):

            image = self.__event2img(X[i])

            if self.problem == "supervised":
                route = self.__saveSupervised(Y[i], i, image)
                imagesRoutesArr.append(route)
            elif self.problem == "unsupervised" or self.problem == "regression":
                route = self.__saveRegressionOrUnsupervised(i, image)
                imagesRoutesArr.append(route)
            else:
                print("Wrong problem definition. Please use 'supervised', 'unsupervised' or 'regression'")
        
        if self.problem == "supervised" :
            data={'images':imagesRoutesArr,'class':Y}
            regressionCSV = pd.DataFrame(data=data)
            regressionCSV.to_csv(self.folder + "/supervised.csv", index=False)
        elif self.problem == "unsupervised":
            data = {'images': imagesRoutesArr}
            regressionCSV = pd.DataFrame(data=data)
            regressionCSV.to_csv(self.folder + "/unsupervised.csv", index=False)
        elif self.problem == "regression":
            data = {'images': imagesRoutesArr,'values':Y}
            regressionCSV = pd.DataFrame(data=data)
            regressionCSV.to_csv(self.folder + "/regression.csv", index=False)
            
    def _testAlg(self, x: pd.DataFrame, y: Union[pd.DataFrame, None]):
        X = x.values
        Y = y.values if y is not None else None

        # Variable for regression problem
        imagesRoutesArr = []

        try:
            os.makedirs(self.folder)
            if self.verbose:
                print("The folder was created " + self.folder + "...")
        except:
            if self.verbose:
                print("The folder " + self.folder + " is already created...")
        for i in range(X.shape[0]):

            image = self.__event2img(X[i])

            if self.problem == "supervised":
                route = self.__saveSupervised(Y[i], i, image)
                imagesRoutesArr.append(route)
            elif self.problem == "unsupervised" or self.problem == "regression":
                route = self.__saveRegressionOrUnsupervised(i, image)
                imagesRoutesArr.append(route)
            else:
                print("Wrong problem definition. Please use 'supervised', 'unsupervised' or 'regression'")
        
        if self.problem == "supervised" :
            data={'images':imagesRoutesArr,'class':Y}
            regressionCSV = pd.DataFrame(data=data)
            regressionCSV.to_csv(self.folder + "/supervised.csv", index=False)
        elif self.problem == "unsupervised":
            data = {'images': imagesRoutesArr}
            regressionCSV = pd.DataFrame(data=data)
            regressionCSV.to_csv(self.folder + "/unsupervised.csv", index=False)
        elif self.problem == "regression":
            data = {'images': imagesRoutesArr,'values':Y}
            regressionCSV = pd.DataFrame(data=data)
            regressionCSV.to_csv(self.folder + "/regression.csv", index=False)
