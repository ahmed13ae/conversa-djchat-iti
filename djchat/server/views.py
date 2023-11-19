from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Category, Server,Channel
from .schema import server_list_docs
from .serializer import CategorySerializer, ServerListSerializer,ChannelSerializer,ServerSerializer


class ChannelViewSet(viewsets.ModelViewSet):
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()

class CategoryViewSet(viewsets.ViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (AllowAny,)

    def list(self, request,*args, **kwargs):
        # GET method for retrieving all categories
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        # POST method for creating a new category
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        # GET method for retrieving a single category by ID
        category = self.queryset.get(pk=pk)
        serializer = self.serializer_class(category)
        return Response(serializer.data)

    def update(self, request, pk=None):
        # PUT method for updating a category by ID
        category = self.queryset.get(pk=pk)
        serializer = self.serializer_class(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        # PATCH method for partially updating a category by ID
        category = self.queryset.get(pk=pk)
        serializer = self.serializer_class(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # DELETE method for deleting a category by ID
        category = self.queryset.get(pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ServerMemebershipViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, server_id):
        server = get_object_or_404(Server, id=server_id)

        user = request.user

        if server.member.filter(id=user.id).exists():
            return Response({"error": "User is already a member"}, status=status.HTTP_409_CONFLICT)

        server.member.add(user)

        return Response({"message": "User joined server successfully"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["DELETE"])
    def remove_member(self, request, server_id):
        server = get_object_or_404(Server, id=server_id)
        user = request.user

        if not server.member.filter(id=user.id).exists():
            return Response({"error": "User is not a member"}, status=status.HTTP_404_NOT_FOUND)

        if server.owner == user:
            return Response({"error": "Owners cannot be removed as a member"}, status=status.HTTP_409_CONFLICT)

        server.member.remove(user)

        return Response({"message": "User removed from server..."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def is_member(self, request, server_id=None):
        server = get_object_or_404(Server, id=server_id)
        user = request.user

        is_member = server.member.filter(id=user.id).exists()

        return Response({"is_member": is_member})


class CategoryListViewSet(viewsets.ViewSet):
    queryset = Category.objects.all()

    @extend_schema(responses=CategorySerializer)
    def list(self, request):
        serializer = CategorySerializer(self.queryset, many=True)
        return Response(serializer.data)


class ServerListViewSet(viewsets.ViewSet):
    queryset = Server.objects.all()
    # permission_classes = [IsAuthenticated]

    @server_list_docs
    def list(self, request):
        """Returns a list of servers filtered by various parameters.

        This method retrieves a queryset of servers based on the query parameters
        provided in the `request` object. The following query parameters are supported:

        - `category`: Filters servers by category name.
        - `qty`: Limits the number of servers returned.
        - `by_user`: Filters servers by user ID, only returning servers that the user is a member of.
        - `by_serverid`: Filters servers by server ID.
        - `with_num_members`: Annotates each server with the number of members it has.

        Args:
        request: A Django Request object containing query parameters.

        Returns:
        A queryset of servers filtered by the specified parameters.

        Raises:
        AuthenticationFailed: If the query includes the 'by_user' or 'by_serverid'
            parameters and the user is not authenticated.
        ValidationError: If there is an error parsing or validating the query parameters.
            This can occur if the `by_serverid` parameter is not a valid integer, or if the
            server with the specified ID does not exist.

        Examples:
        To retrieve all servers in the 'gaming' category with at least 5 members, you can make
        the following request:

            GET /servers/?category=gaming&with_num_members=true&num_members__gte=5

        To retrieve the first 10 servers that the authenticated user is a member of, you can make
        the following request:

            GET /servers/?by_user=true&qty=10

        """
        category = request.query_params.get("category")
        qty = request.query_params.get("qty")
        by_user = request.query_params.get("by_user") == "true"
        by_serverid = request.query_params.get("by_serverid")
        with_num_members = request.query_params.get("with_num_members") == "true"

        if category:
            self.queryset = self.queryset.filter(category__name=category)

        if by_user:
            if by_user and request.user.is_authenticated:
                user_id = request.user.id
                self.queryset = self.queryset.filter(member=user_id)
            else:
                raise AuthenticationFailed()

        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count("member"))

        if by_serverid:
            # if not request.user.is_authenticated:
            #     raise AuthenticationFailed()

            try:
                self.queryset = self.queryset.filter(id=by_serverid)
                if not self.queryset.exists():
                    raise ValidationError(detail=f"Server with id {by_serverid} not found")
            except ValueError:
                raise ValidationError(detail="Server value error")

        if qty:
            self.queryset = self.queryset[: int(qty)]

        serializer = ServerListSerializer(self.queryset, many=True, context={"num_members": with_num_members})
        return Response(serializer.data)
    
class ServerViewSet(viewsets.ViewSet):
    serializer_class = ServerSerializer
    queryset = Server.objects.all()

    def create(self, request, *args, **kwargs):
        """
          Create a new server.

            **Args:**
                request (Request): The HTTP request object containing the server data.

            **Returns:**
                Response: A JSON response containing the created server data or validation errors.

            **Raises:**
                N/A

            **Example:**
                The following example demonstrates how to create a new server using a POST request:

                ```bash
                POST /api/server/create
                {
                    "name": "My Server",
                    "category": "Gaming",
                    "description": "A gaming community server",
                    "members": ["user1", "user2"],
                    "banner": upload image,
                    "icon": upload icon,
                }
                ```

            Note:
                This method uses the ServerSerializer for data validation and saving. If the provided data is
                valid, the server is saved, and a response with the server data and HTTP status 201 Created is returned.
                If there are validation errors, a response with the errors and HTTP status 400 Bad Request is returned.
        """
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        """
        Update a server instance.

        Args:
            request (Request): The HTTP request object containing the updated server data.
            pk (int): The primary key of the server.

        Returns:
            Response: A JSON response containing the updated server data or validation errors.

        Raises:
            N/A
        """
        server = self.get_object(pk)
        serializer = self.serializer_class(server, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # def partial_update(self, request, pk=None):
    #     """
    #     Partially update a server instance.

    #     Args:
    #         request (Request): The HTTP request object containing the partially updated server data.
    #         pk (int): The primary key of the server.

    #     Returns:
    #         Response: A JSON response containing the partially updated server data or validation errors.

    #     Raises:
    #         N/A
    #     """
    #     server = self.get_object(pk)
    #     serializer = self.serializer_class(server, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """
        Destroy a server instance.

        Args:
            request (Request): The HTTP request object.
            pk (int): The primary key of the server.

        Returns:
            Response: A 204 No Content response or a 404 Not Found response.

        Raises:
            N/A
        """
        server = self.get_object(pk)
        server.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get_object(self, pk):
        try:
            return Server.objects.get(pk=int(pk))
        except Server.DoesNotExist:
            raise Http404
    

