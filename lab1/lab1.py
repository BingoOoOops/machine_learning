import numpy as np
from matplotlib import pyplot as plt


def generateData(number, scale=0.5):
    """ Generate training or test data.
    Args:
        number: data number you want which is an integer
        scale: the variance of Gaussian diribution for noise.
    Returns:
        X: a one-dimensional array containing all uniformly distributed x.
        T: sin(2 * pi * x) with Gaussian distribution noise with variance of scale. 
    """
    assert isinstance(number, int)
    assert number > 0
    assert scale > 0
    X = np.linspace(0, 1, num=number)
    T = np.sin(2 * np.pi * X) + np.random.normal(scale=scale, size=X.shape)
    return X, T


def transform(X, degree=2):
    """
    Transform an array to (len(X), degree + 1) matrix.
    Args:
        X: an ndarray.
        degree:int, degree for polynomial.
    Returns:
        for example, [a b] -> [[1 a a^2] [1 b b^2]]
    """
    assert isinstance(degree, int)
    assert X.ndim == 1
    X_T = X.transpose()
    X = np.transpose([X])
    features = [np.ones(len(X))]
    for i in range(0, degree):
        features.append(np.multiply(X_T, features[i]))

    return np.asarray(features).transpose()


def fitting(X_training, T_training):
    """ 求解析解 不带惩罚项 """
    w_analytical_with_regulation = np.dot(
        np.linalg.pinv(X_training), T_training)
    return w_analytical_with_regulation


def fitting_with_regulation(X_training, T_training, hyperparameter=np.exp(-18)):
    """ 求解析解 带惩罚项 """
    X_T = X_training.transpose()
    # w_analytical_with_regulation = np.linalg.pinv(np.dot(X_T, X_training) + np.eye(len(X_T)) * hyperparameter) @ X_T @ T_training
    w_analytical_with_regulation = np.linalg.solve(np.eye(len(X_T)) * hyperparameter +
                                                   np.dot(X_T, X_training), np.dot(X_T, T_training))
    return w_analytical_with_regulation


def predict(X_Test, w):
    return np.dot(X_Test, w)


def h(X_Train, T_training, hyper, number_train, w_0):
    """ 优化函数的导函数 """
    X_T = X_Train.transpose()
    return 1.0 / number_train * (X_T @ X_Train @ w_0 - X_T @ T_training + w_0 * np.exp(hyper))
    # 此处如果增加number_train系数 会使迭代次数增多


def E(X_Train, T_training, hyper, number_train, w_0):
    """ 优化函数 """
    W_T = np.transpose([w_0])
    return 0.5 / number_train * (np.linalg.norm(X_Train @ W_T - T_training) ** 2 + np.exp(hyper) * w_0 @ W_T)


def gradient_descent(X_Train, T_training, hyper, w_0, rate=0.01, delta=1e-6):
    """ 梯度下降法 
    Args:
        hyper:超参数，使用时以np.exp(hyper)为超参数
        rate:学习率
        delta:认为收敛的最小差距
    """
    loss = E(X_Train, T_training, hyper, len(X_Train), w_0)
    k = 0
    while True:
        w_gradient = w_0 - rate * \
            h(X_Train, T_training, hyper, len(X_Train), w_0)
        loss0 = E(X_Train, T_training, hyper, len(X_Train), w_gradient)
        if np.abs(loss0[0] - loss[0]) < delta:
            break
        else:
            print(k)
            k = k + 1
            print("abs:", np.abs(loss - loss0))
            print("loss:", loss)
            loss = loss0
            w_0 = w_gradient
    return w_gradient


def conjugate_gradient(X_Train, T_training, hyper, w_0, delta=1e-6):
    """ 共轭梯度法 """
    X_T = X_Train.transpose()
    b = X_T @ T_training
    A = X_T @ X_Train + np.identity(len(X_T)) * np.exp(hyper)
    r_0 = b - A @ w_0
    w_gradient = w_0
    p = r_0
    k = 0
    while True:
        print(k)
        k = k + 1
        alpha = np.linalg.norm(r_0) ** 2 / (np.transpose(p) @ A @ p)
        print("alpha:", alpha)
        w_gradient = w_gradient + alpha * p
        print("w_gradient:", w_gradient)
        r = r_0 - alpha * A @ p
        # r = b - A @ w_gradient
        print("r:", r)
        # q = np.linalg.norm(A @ w_gradient - b) / np.linalg.norm(b)
        if(np.linalg.norm(r) ** 2 < delta):
            break
        beta = np.linalg.norm(r)**2 / np.linalg.norm(r_0)**2
        print("beta:", beta)
        p = r + beta * p
        print("p:", p)
        r_0 = r
    return w_gradient


number_train = 20  # 训练样本的数量
number_test = 100  # 测试样本的数量
degree = 3  # 多项式的阶数
X_training, T_training = generateData(number_train)
X_test = np.linspace(0, 1, number_test)
X_Train = transform(X_training, degree=degree)
X_Test = transform(X_test, degree=degree)
Y = np.sin(2 * np.pi * X_test)

# 用于解析解(不带正则项)的实验
# title = "degree = " + str(degree) + ", number_train = " + str(number_train) + ", number_test = " + str(number_test)
# plt.title(title)
# plt.ylim(-1.5, 1.5)
# plt.scatter(X_training, T_training, facecolor="none",
#             edgecolor="b", label="training data")
# plt.plot(X_test, predict(X_Test, fitting(X_Train, T_training)), "r", label="analytical solution")
# plt.plot(X_test, Y, "g", label="$\sin(2\pi x)$")
# plt.legend()
# plt.show()

# hyperTestList = []
# hyperList = range(-30, 1)
# for hyper in hyperList:
#     print("hyper = ", hyper)
#     w_analytical_with_regulation = fitting_with_regulation(
#         X_Train, T_training, hyperparameter=np.exp(hyper))
#     T_test = predict(transform(X_test, degree=degree),
#                      w_analytical_with_regulation)
#     loss = Y - T_test
#     ans = np.mean(loss @ np.transpose([loss]))
#     hyperTestList.append(ans)

# bestHyper = hyperList[np.where(hyperTestList == np.min(hyperTestList))[0][0]]

# w_analytical_with_regulation = fitting_with_regulation(
#     X_Train, T_training, hyperparameter=np.exp(bestHyper))
# T_test = predict(X_Test, w_analytical_with_regulation)

# w_0 = np.zeros(degree+1)
# w_gradient = gradient_descent(X_Train, T_training, bestHyper, w_0)
# w_conjugate = conjugate_gradient(X_Train, T_training, bestHyper, w_0)

# print()
# print("hyper:", np.exp(bestHyper), np.min(hyperTestList))
# print("w_analytical_with_regulation(Analytical solution):\n",
#       w_analytical_with_regulation)
# print("w_gradient(Gradient descent):\n", w_gradient)
# print("w_conjugate(Conjugate gradient):\n", w_conjugate)

# plt.figure(figsize=(15, 6))
# plt.subplot(121)
# plt.ylim(-1.5, 1.5)
# plt.scatter(X_training, T_training, facecolor="none",
#             edgecolor="r", label="training data")
# plt.plot(X_test, Y, "g", label="$\sin(2\pi x)$")
# plt.plot(X_test, T_test, "c", label="Analytical solution")
# plt.plot(X_test, predict(X_Test, w_gradient), "r", label="Gradient descent")
# plt.legend()

# plt.subplot(122)
# plt.ylim(-1.5, 1.5)
# plt.scatter(X_training, T_training, facecolor="none",
#             edgecolor="r", label="training data")
# plt.plot(X_test, Y, "g", label="$\sin(2\pi x)$")
# plt.plot(X_test, T_test, "c", label="Analytical solution")
# plt.plot(X_test, predict(X_Test, w_conjugate), "m", label="Conjugate gradient")
# plt.legend()
# plt.show()
