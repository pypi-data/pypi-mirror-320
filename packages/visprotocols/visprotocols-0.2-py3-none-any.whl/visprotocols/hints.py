from abc import ABC


class S7DB(ABC):

    def EnsureConnected(self):
        pass

    def Disconnect(self):
        pass

    def GetName(self) -> str:
        pass

    def ReadBool(self, dbNumber: int, index: int, bit: int) -> bool:
        pass

    def WriteBool(self, dbNumber: int, index: int, bit: int, value: bool):
        pass

    def ReadByte(self, dbNumber: int, index: int) -> int:
        pass

    def WriteByte(self, dbNumber: int, index: int, value: int):
        pass

    def ReadInt(self, dbNumber: int, index: int) -> int:
        pass

    def WriteInt(self, dbNumber: int, index: int, value: int):
        pass

    def ReadReal(self, dbNumber: int, index: int) -> float:
        pass

    def WriteReal(self, dbNumber: int, index: int, value: float):
        pass

    def ReadString(self, dbNumber: int, index: int, maxLength: int) -> str:
        pass

    def WriteString(self, dbNumber: int, index: int, maxLength: int,
                    value: str):
        pass


class Logger(ABC):

    def Information(self, logmsg: str, group: str):
        pass

    def Warning(self, logmsg: str, group: str):
        pass

    def Error(self, logmsg: str, group: str):
        pass


class HIKProc(ABC):

    def LoadProc(self, procName: str) -> object:
        pass

    def SetInputInt(self, vmProcedure: object, name: str, value: int):
        pass

    def SetInputString(self, vmProcedure: object, name: str, value: str):
        pass

    def SetInputFloat(self, vmProcedure: object, name: str, value: float):
        pass

    def GetOutputInt(self, vmProcedure: object, name: str) -> int:
        pass

    def GetOutputString(self, vmProcedure: object, name: str) -> str:
        pass

    def GetOutputFloat(self, vmProcedure: object, name: str) -> float:
        pass


class MkProc(ABC):

    def Trigger(self, procName: str, cmd: str) -> str:
        pass
    
class CancellationToken(ABC):
    IsCancellationRequested: bool
    CanBeCanceled: bool
